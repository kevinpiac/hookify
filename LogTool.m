//
//  LogTool.m
//
//
//  Created by Kevin Piacentini on 02/10/2019.
//

#import <Foundation/Foundation.h>
#import <objc/runtime.h>

@interface LogTool: NSObject
@property int numberOfTabs;

+ (LogTool *)sharedInstance;
+ (void)fileLog: (NSString*)string;
+ (void)debugNSData: (NSData *)data;
+ (void)logDataFromNSString: (NSString *)logContent;
+ (void)untruncatedNSLog:(NSString *)logString;
+ (NSString *)prepend: (int)count string: (NSString*)toPrepend toString: (NSString *)originalString;
@end

@implementation LogTool
+(LogTool *)sharedInstance {
    static LogTool *sharedInstance = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        sharedInstance = [[LogTool alloc] init];
        // Do any other initialisation stuff here
        sharedInstance.numberOfTabs = -1;
    });
    return sharedInstance;
}
+ (NSString *)prepend: (int)count string: (NSString*)toPrepend toString: (NSString *)originalString {
    NSString *newString = [NSString stringWithFormat: @"%@", originalString];

    while (count > 0) {
        newString = [NSString stringWithFormat: @"%@%@", toPrepend, newString];
        count--;
    }
    return newString;
}
+ (void)fileLog: (NSString*)string {
    NSFileHandle *file;
    NSData *data;

    file = [NSFileHandle fileHandleForUpdatingAtPath: @"/tmp/filelog.txt"];

    [file seekToEndOfFile];

    NSString *logContent = [string stringByAppendingString:@"\n"];
    data = [logContent dataUsingEncoding:NSUTF8StringEncoding];

    [file writeData: data];

    [file closeFile];
}
+ (void)debugNSData:(NSData *)data
{
    // Convert NSData to NSString
    NSString *output = [[NSString alloc] initWithData:data encoding: NSUTF8StringEncoding];

    NSLog(@"NSData: %@\n%@", output, data);
}
+ (void)untruncatedNSLog:(NSString *)logString {
    int stepLog = 800;
    NSInteger strLen = [@([logString length]) integerValue];
    NSInteger countInt = strLen / stepLog;

    if (strLen > stepLog) {
        for (int i=1; i <= countInt; i++) {
            NSString *character = [logString substringWithRange:NSMakeRange((i*stepLog)-stepLog, stepLog)];
            NSLog(@"%@", character);

        }
        NSString *character = [logString substringWithRange:NSMakeRange((countInt*stepLog), strLen-(countInt*stepLog))];
        NSLog(@"%@", character);
    } else {
        NSLog(@"%@", logString);
    }
}
+ (void)logDataFromNSString: (NSString *)logContent
{
    LogTool *logTool = [LogTool sharedInstance];
    BOOL isBegin = [logContent containsString:@">>>> -"];
    BOOL isEnd = [logContent containsString:@"<<<< -"];
    NSString *toPrint = [NSString stringWithFormat: @"%@", logContent];

    if (isBegin) {
        logTool.numberOfTabs = logTool.numberOfTabs + 1;
        toPrint = [LogTool prepend: logTool.numberOfTabs string: @">>>> " toString: logContent];
    } else if (isEnd) {
        toPrint = [LogTool prepend: logTool.numberOfTabs string: @"<<<< " toString: logContent];
        logTool.numberOfTabs = logTool.numberOfTabs - 1;
    } else {
        toPrint = [LogTool prepend: logTool.numberOfTabs string: @"---- " toString: logContent];
    }
    [LogTool untruncatedNSLog: toPrint];
    [LogTool fileLog: toPrint];
}
@end
