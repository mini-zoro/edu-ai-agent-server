from django.db import models

from AAServer.common.models import BaseModel
from apps.auth.models import User
from apps.code_dict.models import Code
from apps.university.models import University


class Teacher(BaseModel):
    """
    教师模型
    """
    # 个人信息
    id = models.BigIntegerField(primary_key=True, db_comment='教师ID')
    user = models.ForeignKey(User, db_comment='用户ID', on_delete=models.RESTRICT, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True, db_comment='出生日期')
    gender = models.IntegerField(
        choices=[(1, '男'), (0, '女')],
        blank=True, null=True, db_comment='性别'
    )

    # 职业信息
    university = models.ForeignKey(University, on_delete=models.RESTRICT, blank=True, null=True, db_comment='学校')
    subject = models.IntegerField(blank=True, null=True, db_comment='学科，具体以码表为准')
    professional_title = models.IntegerField(null=True, blank=True, db_comment="职称，具体以码表为准")
    profession = models.IntegerField(null=True, blank=True, db_comment="职务, 如教师、教授等，具体以码表为准")
    department = models.CharField(max_length=100, null=True, blank=True, db_comment="部门")

    class Meta:
        db_table = 'tb_teacher'
        db_table_comment = "教师信息表"

    def __str__(self):
        return self.user.name
