import time
def safe_acad_operation(operation, operation_name="AutoCAD操作", max_retries=3, retry_delay=1.5, backoff=1.5):
    """执行 AutoCAD 操作并在遇到繁忙/拒绝错误时重试。

    参数:
        operation: 要执行的可调用对象
        operation_name: 日志中显示的操作名称
        max_retries: 最多尝试次数（至少1）
        retry_delay: 首次重试延迟（秒）
        backoff: 每次重试时延迟的乘数

    返回:
        operation() 的返回值，或在失败时抛出最后一次异常。
    """
    if max_retries < 1:
        max_retries = 1

    busy_indicators = ("-2147418111", "拒绝接收", "繁忙", "2147352567")
    delay = float(retry_delay)
    last_exc = None

    for attempt in range(1, max_retries + 1):
        try:
            return operation()
        except Exception as e:
            last_exc = e
            msg = str(e)
            is_busy = any(ind in msg for ind in busy_indicators)

            if is_busy and attempt < max_retries:
                print(f"  {operation_name} 繁忙，{attempt}/{max_retries}，{delay:.1f}s 后重试...")
                time.sleep(delay)
                delay *= backoff
                continue

            print(f"  {operation_name} 失败: {e}")
            raise

    # 如果循环结束（不太可能），抛出最后的异常
    raise last_exc
