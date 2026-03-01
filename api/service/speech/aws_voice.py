import time
import uuid

import boto3
import requests
from mypy_boto3_polly import PollyClient
from mypy_boto3_s3 import S3Client
from mypy_boto3_transcribe import TranscribeServiceClient


class AWSVoiceService:
    def __init__(self):
        self.s3: S3Client = boto3.client("s3", region_name="ap-south-1")
        self.transcribe_client: TranscribeServiceClient = boto3.client(
            "transcribe", region_name="ap-south-1"
        )
        self.polly: PollyClient = boto3.client("polly", region_name="ap-south-1")
        self.bucket = "kisaanvaani-media-bucket"

    def transcribe(self, audio_bytes):
        job_name = f"kv-{uuid.uuid4()}"
        s3_key = f"input-audio/{job_name}.ogg"

        self.s3.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=audio_bytes,
            ContentType="audio/ogg",
        )

        media_uri = f"s3://{self.bucket}/{s3_key}"

        self.transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": media_uri},
            MediaFormat="ogg",
            IdentifyLanguage=True,
            LanguageOptions=["en-IN", "hi-IN"],
        )

        while True:
            status = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            job_details = status.get("TranscriptionJob", {})
            state = job_details.get("TranscriptionJobStatus")
            if state in ["COMPLETED", "FAILED"]:
                break
            time.sleep(2)

        if state == "FAILED":
            raise Exception("Transcription failed")

        transcript = job_details.get("Transcript") or {}
        transcript_uri = transcript.get("TranscriptFileUri")
        if not transcript_uri:
            raise Exception("Transcription completed without transcript URI")
        transcript_json = requests.get(transcript_uri, timeout=10).json()
        return transcript_json["results"]["transcripts"][0]["transcript"]

    def synthesize(self, text):
        response = self.polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId="Kajal",
            Engine="neural",
        )

        audio_stream = response["AudioStream"].read()
        file_key = f"tts-output/{uuid.uuid4()}.mp3"

        self.s3.put_object(
            Bucket=self.bucket,
            Key=file_key,
            Body=audio_stream,
            ContentType="audio/mpeg",
        )

        return f"s3://{self.bucket}/{file_key}"
