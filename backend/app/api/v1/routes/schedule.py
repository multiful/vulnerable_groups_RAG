# File: schedule.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: 일정·링크 API reserved — HTTP 501 + envelope
from __future__ import annotations

from fastapi import APIRouter, Response

from backend.app.services import schedule_service

router = APIRouter()


@router.get("/schedules/exams/{cert_id}")
def get_exam_schedule(cert_id: str, response: Response) -> dict:
    return schedule_service.reserved_response(response, feature="exam_schedule", cert_id=cert_id)


@router.get("/schedules/applications/{cert_id}")
def get_application_schedule(cert_id: str, response: Response) -> dict:
    return schedule_service.reserved_response(
        response, feature="application_schedule", cert_id=cert_id
    )


@router.get("/links/support/{cert_id}")
def get_support_link(cert_id: str, response: Response) -> dict:
    return schedule_service.reserved_response(response, feature="support_link", cert_id=cert_id)
