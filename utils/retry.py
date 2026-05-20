import time

def retry(operation, operation_name="操作", max_retries=3, initial_delay=1.0):
    """带重试机制的操作执行"""
    for attempt in range(1, max_retries + 1):
        try:
            return operation()
        except Exception as e:
            if attempt < max_retries and ("-2147418111" in str(e) or "拒绝接收" in str(e)):
                print(f"  {operation_name} 繁忙，{attempt}/{max_retries} 次重试...")
                time.sleep(initial_delay)
                continue
            else:
                raise

__version__ = "0.2.0"