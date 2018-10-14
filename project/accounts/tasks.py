from celery import shared_task
import datetime
import glob
import re
import pandas as pd
import pyocr
import pyocr.builders
import subprocess
from copy import deepcopy
from tabula import read_pdf
from PIL import Image
from accounts.models import (
    User, Shift, PDFFile
)


JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
segments = ['X', 'Y', 'Z', 'A', 'B', 'C', 'D']


# ====================
# call function
# ====================
@shared_task
def delete_pdf():
    """
    delete pdf uploaded by leader
    Also, shifts with uploaded pdf are deleted
    """

    today = datetime.datetime.now(JST)
    threem_ago = (today - datetime.timedelta(weeks=12))
    sixm_ago = (today - datetime.timedelta(weeks=16))
    PDFFile.objects.filter(created_at__range=[sixm_ago, threem_ago]).delete()


@shared_task
def shiftregistrations(pdfpk: int, pdfpath: str):
    """
    pdf of shifts format -> shift registration
    """

    pdf = PDFFile.objects.get(pk=pdfpk)
    shifts = __pdf2shift(pdfpath)
    days = __dayimg2num(pdfpath)
    daynum = 0
    before = 0
    for shift in shifts:
        daynum += 1 if segments.index(shift['segment']) < before else 0
        __shiftregistration_oneday(pdf, shift, days[daynum])
        before = segments.index(shift['segment'])

# ====================
# support function
# ====================


def __shiftregistration_oneday(pdf, shift: dict, day: datetime.datetime):
    """
    regist shift to DB
    @param <dict> shift               : shift  of dict format
    @param <datetime.datetime> day    : day of string format
    """

    segment = shift['segment']
    handle_lists = shift['shifts']
    for handle in handle_lists:
        teacher = handle['name'].split()
        user = User.objects.all().filter(last_name=teacher[0],
                                         first_name=teacher[1])
        if len(user) <= 0:
            continue
        user = user[0]
        for student in handle['students']:
            shift = Shift.objects.create(pdf_id=pdf, user_id=user,
                                         day=day, segment=segment,
                                         student_name=student['name'],
                                         subject_name=student['class'],
                                         student_grade=student['grade'])
            shift.save()


def __pdf2shift(pdfpath: str) -> list:
    """
    pdf of shifts format -> shifts
    @param <str> pdfpath : pdf path
    @return <list>       : shifts
    """

    df = read_pdf(pdfpath, pages="all", multiple_tables=True)
    shifts = [pd2shift(df[i]) for i in range(len(df))]
    return shifts


def __dayimg2num(pdfpath: str) -> list:
    """
    day images in pdf of shifts format -> day
    @param <str> pdfpath : pdf path
    @return <list>       : days
    """

    dirpath = pdfpath[:pdfpath.rfind("/") + 1]
    subprocess.call(['pdftohtml', '-c', '-xml', pdfpath, dirpath + 'output.xml'])
    days = [get_digit_ocr_info(path)
            for path in glob_sorted_with_number(dirpath + 'output-*_3.png')]
    return days


def get_digit_ocr_info(path: str) -> datetime.datetime:
    """
    day image in a shift -> day string
    @param <str> path : path of day image in a shift
    @param <str>      : day of datetime format
    """

    img = Image.open(path)

    width, height = img.size

    tools = pyocr.get_available_tools()
    tool = tools[0]
    # langs = tool.get_available_languages()
    lang = 'jpn'

    digit_txt = tool.image_to_string(
        img,
        lang=lang,
        builder=pyocr.builders.DigitBuilder(tesseract_layout=6)
    )

    day = digit_txt.replace('ー', '1').split()
    dt_now = datetime.datetime.now(JST)
    year = dt_now.year if dt_now.month <= int(day[0]) else dt_now.year + 1

    return datetime.datetime(year, int(day[0]), int(day[1]), tzinfo=JST)


def pd2shift(df: pd.DataFrame) -> dict:
    """
    shift of pandas format -> shift of list format
    @param <pd.DataFrame> df : DataFrame of shift
    @return <dict>           : {segment: 'c',
                                shift: [{'name': , '...', 'students': ['...']}]}
    """

    shiftdict = {}

    # extraction segment
    row1 = df[:1]
    for i, row in enumerate(row1):
        if not row1[i].isnull().values[0]:
            seg = row1[i].values[0]
            break

    shiftlist = []
    # extraction teacher name, student name, student grade etc.
    student = {'name': '', 'class': '', 'grade': ''}
    teacher = {'name': '', 'students': []}
    for i in range(len(df)):
        elems = df[i][1:].values
        if not any(elems == elems):
            break
        if i % 2 == 0:
            newteacher = deepcopy(teacher)
            newteacher['name'] = elems[0]
            for elem in elems[1:]:
                if type(elem) != str:
                    continue
                s = re.sub(r'\d+', '', elem).split()
                name = s[0] + s[1]
                class_ = s[2]
                newstudent = deepcopy(student)
                newstudent['name'] = name
                newstudent['class'] = class_
                newteacher['students'].append(newstudent)
        else:
            for j, elem in enumerate(elems[1:]):
                if type(elem) != str:
                    continue
                newteacher['students'][j]['grade'] = elem
            shiftlist.append(newteacher)
    return {'segment': seg, 'shifts': shiftlist}


def glob_sorted_with_number(path):
    return sorted(glob.glob(path), key=numerical_sort)


def numerical_sort(value):
    numbers = re.compile(r"(\d+)")
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts
