from app.parser.email_parser import EmailParser


def test_parser_extracts_core_fields_and_attachment():
    raw = b"""From: Alice <alice@example.com>
To: Bob <bob@example.com>
Subject: Test Email
Message-ID: <abc@example.com>
Date: Tue, 01 Sep 2026 10:00:00 +0530
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=BOUNDARY

--BOUNDARY
Content-Type: text/plain; charset=utf-8

Hello Bob
--BOUNDARY
Content-Type: text/plain
Content-Disposition: attachment; filename=note.txt

attachment data
--BOUNDARY--
"""

    parsed = EmailParser().parse(raw)

    assert parsed.subject == "Test Email"
    assert parsed.message_id == "<abc@example.com>"
    assert parsed.from_address.address == "alice@example.com"
    assert parsed.to[0].address == "bob@example.com"
    assert "Hello Bob" in parsed.body_text
    assert len(parsed.attachments) == 1
    assert parsed.attachments[0].filename == "note.txt"
