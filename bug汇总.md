🐛 GLM5 新引入的 Bug
                      
  Bug A: query_db_processlist 重复 except 块（mysql_adapter.py:104-121）
                                                                                                                                                                                     
  try:
      rows = await asyncio.to_thread(...)                                                                                                                                            
      ...                                                                                                                                                                            
      return {...}
  except Exception as e:        # 第一个 except (line 104) ✓                                                                                                                         
      logger.error(...)                                                                                                                                                              
      return {...}
  except Exception as e:        # 第二个 except (line 113) ✗ DEAD CODE                                                                                                               
      logger.error(...)                                                                                                                                                              
      return {...}
                                                                                                                                                                                     
  第二个 except 永远不会被执行（第一个已经捕获了所有 Exception）。Python 不会报语法错误，但这是明显的复制粘贴遗漏，应该删掉 line 113-121。                                           
   
  ---                                                                                                                                                                                
  ⚠️  仍然遗留的问题
                   
  Issue 1: truncate_result 截断后破坏 logs 类型契约
                                                                                                                                                                                     
  truncate_result 截断时会返回 {"_truncated": True, "raw_preview": "..."}（dict，不是 list）。然后：                                                                                 
                                                                                                                                                                                     
  logs = truncate_result(logs)   # logs 现在可能是 dict                                                                                                                              
  return {                                                                                                                                                                           
      "logs": logs,              # 契约说应该是 list，现在变 dict
      "count": len(logs) if isinstance(logs, list) else 0,  # count=0                                                                                                                
      "query": query,                                                                                                                                                                
  }                                                                                                                                                                                  
                                                                                                                                                                                     
  下游代码 for log in result["logs"] 会拿到 dict 的 keys，行为完全错乱。                                                                                                             
   
  修复建议：在 query_logs_from_db 内部按条数截断，而不是按字节：                                                                                                                     
                  
  # 替代 truncate_result(logs)                                                                                                                                                       
  MAX_BYTES = 64 * 1024
  import json                                                                                                                                                                        
  while logs and len(json.dumps(logs, ensure_ascii=False, default=str).encode()) > MAX_BYTES:
      logs.pop()  # 从尾部丢弃直到符合大小                                                                                                                                           
                                                                                                                                                                                     
  或者保持类型契约，加 _truncated 标志位：                                                                                                                                           
                                                                                                                                                                                     
  truncated_flag = False                                                                                                                                                             
  while logs and len(json.dumps(logs, default=str).encode()) > MAX_BYTES:                                                                                                            
      logs.pop()                                                                                                                                                                     
      truncated_flag = True                                                                                                                                                          
  return {"logs": logs, "count": len(logs), "query": query, "truncated": truncated_flag}                                                                                             
                                                                                                                                                                                     
  Issue 2: 5.1 三个工具的签名 vs gateway 调用约定不匹配（pre-existing bug）                                                                                                          
                                                                                                                                                                                     
  不是 5.1.5 的问题，但同文件，顺便指出：                                                                                                                                            
                  
  query_db_slow_queries / query_db_table_status / query_db_variables 的签名都是 params: Dict[str, Any] = None，但 gateway.py:333 用 handler(**params)                                
  调用——这会把请求参数解构成关键字参数。
                                                                                                                                                                                     
  举例：当 LLM 调用 query_db_slow_queries(threshold_seconds=10) 时：                                                                                                                 
  - gateway 实际执行：handler(threshold_seconds=10)
  - 但函数签名是 query_db_slow_queries(params=None)                                                                                                                                  
  - 结果：TypeError: unexpected keyword argument 'threshold_seconds'
                                                                                                                                                                                     
  只有不传任何参数时才能跑起来。                                                                                                                                                     
                                                                                                                                                                                     
  修复：把这三个函数的签名都改成与 query_db_processlist 一致的 **kwargs：                                                                                                            
                  
  async def query_db_slow_queries(**kwargs) -> Dict[str, Any]:                                                                                                                       
      threshold = kwargs.get("threshold_seconds", 5)                                                                                                                                 
      ...
                                                                                                                                                                                     
  ---                                                                                                                                                                                
  小问题（可忽略）
                                                                                                                                                                                     
  - mysql_adapter.py:2 导入了 time 但没用到
  - truncate_result 本身的 json.loads(truncated + '"}]}') hack 很脆弱，几乎肯定会 fallback 到 {_truncated: True, ...} 分支                                                           
                                                                                                                                                                                     
  ---                                                                                                                                                                                
  优先级                                                                                                                                                                             
                  
  1. P0：Bug A（删除重复 except 块）
  2. P0：Issue 2（修 5.1 三个函数签名，否则 5.1 工具被 LLM 调用必崩）                                                                                                                
  3. P1：Issue 1（按条数截断而非字节）              