## Getting started

Hookify ouputs a hooked version of each methods contained in a header file provided by classdump utility.
Each method contained in the header file will be hooked in order to output ```>>>BEGIN [ClassName MethodName paramValue1 paramValue2...]``` and ```<<< END [ClassName MethodName]``` each time is called by the app.
It allows you to follow the flow of each processes and gather all this data in a filelog.txt located on your iOS device.

### Create your log tweak file

Create a your_tweak.xm tweak file as usualy and add the following snippet of code. This is a small interface which allows your tweak to "console.log" data inside a file located on your iOS device while the app is running.
Since hookify uses this it's required.

``` objective-c
// your_tweak.xm
@interface logTool: NSObject
+ (void)logDataFromNSString: (NSString *)logContent;
@end

@implementation logTool
+ (void)logDataFromNSString: (NSString *)logContent
{
    NSFileHandle *file;
    NSData *data;

    file = [NSFileHandle fileHandleForUpdatingAtPath: @"/tmp/filelog.txt"];

    [file seekToEndOfFile];

    logContent = [logContent stringByAppendingString:@"\n------------\n"];
    data = [logContent dataUsingEncoding:NSUTF8StringEncoding];

    [file writeData: data];

    [file closeFile];
}
@end


```

Once it's done you can use hookify to generate hooked methods.


``` sh
python hookify.py ./path_to_your_header_generated_with_classdump.h >> your_tweak.xm
```

Sample output in your_tweak.xm
``` objective-c

+ (void)logMediaDownloadEventWithRequest:(id)arg1 response:(id)arg2 parameters:(id)arg3 {[logTool logDataFromNSString:@">>>> BEGIN - [SCAPIClient logMediaDownloadEventWithRequest]"];%orig;[logTool logDataFromNSString:@"<<<< END - [SCAPIClient logMediaDownloadEventWithRequest]"]; }
- (void)observeValueForKeyPath:(id)arg1 ofObject:(id)arg2 change:(id)arg3 context:(void *)arg4 {[logTool logDataFromNSString:@">>>> BEGIN - [SCAPIClient observeValueForKeyPath]"];%orig;[logTool logDataFromNSString:@"<<<< END - [SCAPIClient observeValueForKeyPath]"]; }
- (void)enqueueHTTPRequestOperation:(id)arg1 {[logTool logDataFromNSString:@">>>> BEGIN - [SCAPIClient enqueueHTTPRequestOperation]"];%orig;[logTool logDataFromNSString:@"<<<< END - [SCAPIClient enqueueHTTPRequestOperation]"]; }
```
