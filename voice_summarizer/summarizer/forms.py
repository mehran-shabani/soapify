"""Forms for the summarizer app."""
from __future__ import annotations

from django import forms

ALLOWED_EXTENSIONS: tuple[str, ...] = (
    ".mp3",
    ".wav",
    ".m4a",
    ".aac",
    ".ogg",
    ".flac",
    ".webm",
)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


class UploadAudioForm(forms.Form):
    """Simple upload form for lecture audio."""

    file = forms.FileField(
        label="فایل صوتی (حدوداً تا ۵ دقیقه)",
        allow_empty_file=False,
        help_text="فایل‌های mp3، wav، m4a، aac، ogg، flac یا webm با حداکثر حجم ۱۰ مگابایت",
    )

    def clean_file(self) -> forms.FileField:
        uploaded = self.cleaned_data["file"]
        extension = self._get_extension(uploaded.name)
        if extension not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                "فرمت فایل پشتیبانی نمی‌شود. لطفاً یکی از پسوندهای مجاز را بارگذاری کنید."
            )
        if uploaded.size and uploaded.size > MAX_FILE_SIZE_BYTES:
            raise forms.ValidationError("حجم فایل بیش از ۱۰ مگابایت است. لطفاً فایل کوچک‌تری انتخاب کنید.")
        return uploaded

    @staticmethod
    def _get_extension(filename: str) -> str:
        return ("." + filename.split(".")[-1].lower()) if "." in filename else ""
