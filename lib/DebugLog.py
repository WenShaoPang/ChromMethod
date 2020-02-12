# coding: utf-8
"""
參考資料:

https://stackoverflow.com/questions/34467701/decorating-methods-attributeerror-function-object-has-no-attribute-self

https://www.twblogs.net/a/5cd46590bd9eee67a77f34b9
"""
import sys
import traceback

level = 'Debug'
class logging(object):
    instance_ = None
    def __init__(self, func):
        self.func = func
        self.level = level

    def __get__(self, instance, owner):
        self.instance_ = instance
        return self.__call__

    def __call__(self, *args, **kwargs):
        """Invoked on every call of any decorated method"""
        '''
        # set attribute directly within bound method
        bound_method = getattr(self.instance_, self.func.__name__)
        bound_method.__dict__['called'] = datetime.utcnow()
        '''
        print( "[{level}]: enter function {func}()".format(
            level=self.level,
            func=self.func.__name__)
        )

        # returning original function with class' instance as self
        try:
            if self.instance_ == None:
                return self.func(*args, **kwargs)
            else:
                return self.func(self.instance_, *args, **kwargs)
        except Exception as e:
            print('Error in {func} : {error}'.format(func=self.func,error=e))
            error_class = e.__class__.__name__ #取得錯誤類型
            detail = e.args[0] #取得詳細內容
            cl, exc, tb = sys.exc_info() #取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            fileName = lastCallStack[0] #取得發生的檔案名稱
            lineNum = lastCallStack[1] #取得發生的行號
            funcName = lastCallStack[2] #取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            print(errMsg)
            return 0





        
        