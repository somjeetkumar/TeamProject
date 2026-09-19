
from celery import shared_task
from django.core.mail import send_mail

MAIL_CONTENT = {
    "Task assigned": {
        "subject": "Task Assigned to You",
        "template": "You have been assigned a new task:- {content}"
    },

    "Task completed": {
        "subject": "Task Completed",
        "template": "The task has been completed:- {content}"
    },

    "Comment added": {
        "subject": "New Comment Added",
        "template": "A new comment was added:- {content}"
    },
}





# @shared_task
# def notification_email(mail,Mtype):
#     send_mail(
#         MAIL_CONTENT[Mtype]["subject"],
#         MAIL_CONTENT[Mtype]["template"],
#         "somjeetkumar30@mail.com",
#         [mail],
#     )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def notification_email(self,mail, Mtype, content):
    mail_data = MAIL_CONTENT[Mtype]

    message = mail_data["template"].format(content=content)

    send_mail(
        mail_data["subject"],
        message,
        "somjeetkumar30@gmail.com",
        [mail],
    )