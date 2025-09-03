from django.db import models

from AAServer.common.models import BaseModel


class University(BaseModel):
    school_name = models.CharField(max_length=255, null=True, blank=True, db_comment="学校名称")
    school_id_code = models.CharField(max_length=255, null=True, blank=True, db_comment="学校标识码")
    authorities = models.CharField(max_length=255, null=True, blank=True, db_comment="主管部门")
    location = models.CharField(max_length=255, null=True, blank=True, db_comment="所在地")
    edu_level = models.CharField(max_length=255, null=True, blank=True, db_comment="办学层次")
    remarks = models.CharField(max_length=255, null=True, blank=True, db_comment="备注")

    class Meta:
        db_table = 'tb_university'
        db_table_comment = '高校信息表'

