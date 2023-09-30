from ..dependencies import CheckHttpFileType


def CheckLessonType(url: str) -> str:
    filetype = CheckHttpFileType(url)
    if filetype == "video":
        return "video"
    else:
        return "file"
    # TODO: quiz type
