autoops:
  -  底层基于分布式任务队列Celery+redbeat实现
  -  通过对task进行统一抽象，实现了自定义task，并支持动态增加task、删除task，修改task
  -  目前支持任务定时调度执行，支持crontab表达式、以及interval定时器
  -  支持通过api触发任务，并通过任务id异步获取结果
  -  集成了webssh功能，支持直接通过we管理远程机器
  -  集成了ansible API，支持更多的运维自动化管理

important:
   - celery 版本需要使用requirements.txt 指定的版本，否则可能出现时区问题，导致任务导读异常