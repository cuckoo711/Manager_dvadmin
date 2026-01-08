"""
Creation Date: 2025/1/8
Creation Time: 上午4:04
Dir Path: backend/apps/gamebackend/dslhbackend
Project Name: Manager_dvadmin_my
File Name: tasks.py
Editor: cuckoo
"""
import json

from application.celery import app
from apps.gamebackend.dslhbackend.models import DSLHMergeTask
from apps.gamebackend.dslhbackend.utils.Merger import ServerMerger


@app.task
def async_merge_task(task_id, *args, **kwargs):
    merger_task: DSLHMergeTask = DSLHMergeTask.objects.get(id=task_id)
    merger_task.start()

    merger = ServerMerger(
        remote_ip=merger_task.remote_ip,
        mysql_password=merger_task.mysql_password,
        prefix=merger_task.prefix,
        start_id=merger_task.start_id,
        end_id=merger_task.end_id,
        dest_id=merger_task.dest_id,
        merge_ids=merger_task.merge_ids,
        merged_ids=merger_task.merged_ids,
        remote_password=merger_task.remote_password,
        output_dir=merger_task.output_dir
    )
    merger_task.add_log("合服任务初始化成功, 开始生成脚本")
    merger.generate_scripts()
    merger_task.add_log(f"脚本生成成功, 路径标识: {merger_task.output_dir}\n开始合服")
    try:
        merger.merge()
        merger_task.add_log(f"合服成功, 日志:\n{json.dumps(merger.logs, ensure_ascii=False, indent=4)}")
        merger_task.finish()
    except Exception as e:
        merger_task.add_log(f"合服失败: {e}")
        merger_task.add_log(f"日志:\n{json.dumps(merger.logs, ensure_ascii=False, indent=4)}")
        merger_task.fail()
