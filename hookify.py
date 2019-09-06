#!/usr/bin/env python

import os
import re
import sys
import glob
import getopt

from regexp import *

#Should remove
KNOWN_TYPES = [
    'id', 'NSObject', 'void', 'char', 'int', 'unsigned', 'double', 'float', 'long', 'bool', 'BOOL', '_Bool',
    'NSAffineTransform','NSAppleEventDescriptor','NSAppleEventManager','NSAppleScript',
    'NSArchiver','NSArray','NSAssertionHandler','NSAttributedString','NSAutoreleasePool',
    'NSBlockOperation','NSBundle','NSCache','NSCachedURLResponse','NSCalendar','NSCharacterSet',
    'NSClassDescription','NSCloneCommand','NSCloseCommand','NSCoder','NSComparisonPredicate',
    'NSCompoundPredicate','NSCondition','NSConditionLock','NSConnection','NSCountCommand',
    'NSCountedSet','NSCreateCommand','NSData','NSDataDetector','NSDate','NSDateComponents',
    'NSDateFormatter','NSDecimalNumber','NSDecimalNumberHandler','NSDeleteCommand','NSDictionary',
    'NSDirectoryEnumerator','NSDistantObject','NSDistantObjectRequest','NSDistributedLock',
    'NSDistributedNotificationCenter','NSEnumerator','NSError','NSException','NSExistsCommand',
    'NSExpression','NSFileCoordinator','NSFileHandle','NSFileManager','NSFileVersion','NSFileWrapper',
    'NSFormatter','NSGarbageCollector','NSGetCommand','NSHashTable','NSHost','NSHTTPCookie',
    'NSHTTPCookieStorage','NSHTTPURLResponse','NSIndexPath','NSIndexSet','NSIndexSpecifier','NSInputStream',
    'NSInvocation','NSInvocationOperation','NSKeyedArchiver','NSKeyedUnarchiver','NSLinguisticTagger',
    'NSLocale','NSLock','NSLogicalTest','NSMachBootstrapServer','NSMachPort','NSMapTable','NSMessagePort',
    'NSMessagePortNameServer','NSMetadataItem','NSMetadataQuery','NSMetadataQueryAttributeValueTuple',
    'NSMetadataQueryResultGroup','NSMethodSignature','NSMiddleSpecifier','NSMoveCommand','NSMutableArray',
    'NSMutableAttributedString','NSMutableCharacterSet','NSMutableData','NSMutableDictionary',
    'NSMutableIndexSet','NSMutableOrderedSet','NSMutableSet','NSMutableString','NSMutableURLRequest',
    'NSNameSpecifier','NSNetService','NSNetServiceBrowser','NSNotification','NSNotificationCenter',
    'NSNotificationQueue','NSNull','NSNumber','NSNumberFormatter','NSObject','NSOperation','NSOperationQueue',
    'NSOrderedSet','NSOrthography','NSOutputStream','NSPipe','NSPointerArray','NSPointerFunctions','NSPort',
    'NSPortCoder','NSPortMessage','NSPortNameServer','NSPositionalSpecifier','NSPredicate','NSProcessInfo',
    'NSPropertyListSerialization','NSPropertySpecifier','NSProtocolChecker','NSProxy','NSQuitCommand',
    'NSRandomSpecifier','NSRangeSpecifier','NSRecursiveLock','NSRegularExpression','NSRelativeSpecifier',
    'NSRunLoop','NSScanner','NSScriptClassDescription','NSScriptCoercionHandler','NSScriptCommand',
    'NSScriptCommandDescription','NSScriptExecutionContext','NSScriptObjectSpecifier','NSScriptSuiteRegistry',
    'NSScriptWhoseTest','NSSet','NSSetCommand','NSSocketPort','NSSocketPortNameServer','NSSortDescriptor',
    'NSSpecifierTest','NSSpellServer','NSStream','NSString','NSTask','NSTextCheckingResult','NSThread',
    'NSTimer','NSTimeZone','NSUbiquitousKeyValueStore','NSUnarchiver','NSUndoManager','NSUniqueIDSpecifier',
    'NSURL','NSURLAuthenticationChallenge','NSURLCache','NSURLConnection','NSURLCredential','NSURLCredentialStorage',
    'NSURLDownload','NSURLHandle','NSURLProtectionSpace','NSURLProtocol','NSURLRequest','NSURLResponse',
    'NSUserAppleScriptTask','NSUserAutomatorTask','NSUserDefaults','NSUserNotification','NSUserNotificationCenter',
    'NSUserScriptTask','NSUserUnixTask','NSUUID','NSValue','NSValueTransformer','NSWhoseSpecifier','NSXMLDocument',
    'NSXMLDTD','NSXMLDTDNode','NSXMLElement','NSXMLNode','NSXMLParser','NSXPCConnection','NSXPCInterface',
    'NSXPCListener','NSXPCListenerEndpoint','NSCoding','NSComparisonMethods','NSConnectionDelegate','NSCopying',
    'NSDecimalNumberBehaviors','NSErrorRecoveryAttempting','NSFastEnumeration','NSFileManagerDelegate',
    'NSFilePresenter','NSKeyedArchiverDelegate','NSKeyedUnarchiverDelegate','NSKeyValueCoding','NSKeyValueObserving',
    'NSLocking','NSMachPortDelegate','NSMetadataQueryDelegate','NSMutableCopying','NSNetServiceBrowserDelegate',
    'NSNetServiceDelegate', 'NSPortDelegate','NSScriptingComparisonMethods','NSScriptKeyValueCoding',
    'NSScriptObjectSpecifiers','NSSecureCoding','NSSpellServerDelegate','NSStreamDelegate',
    'NSURLAuthenticationChallengeSender','NSURLConnectionDataDelegate','NSURLConnectionDelegate',
    'NSURLConnectionDelegate','NSURLHandleClient','NSURLProtocolClient','NSUserNotificationCenterDelegate',
    'NSXMLParserDelegate','NSXPCListenerDelegate','NSXPCProxyCreating', 'CBCentralManager', 'CBPeripheral',
]

def map_format_specifier(type):
    map = {
        "int": "%d",
        "BOOL": "%u",
        "_Bool": "%u",
        "bool": "%u",
        "unsigned int": "%u",
        "long long": "%lld",
        "float": "%f",
        "double": "%f",
        "unsigned char": "%c",
        "unichar": "%C",
        "unsigned long long": "%llu",
        "short": "%hd",
        "unsigned short": "%hu",
    }
    specifier = map.get(type)
    if specifier:
        return specifier
    if type_pointer_regex().search(type):
        return "%p"
    else:
        return "%@"

class ObjcMethod():
    def __init__(self, line, interface):
        # TODO: do replacement in one single line...
        self.skip = False
        self.line = type_unknown_regex().sub("id", line);
        self.line = struct_regex().sub("id", self.line)
        self.ret_type = self.get_ret_type()
        self.interface = interface
        self.name = self.get_name()
        self.full_name = "[%s %s]" %(interface, self.name)
        if avoided_pointer_regex().search(self.line):
            self.skip = True
            return

    def get_name(self):
        splits = self.line.split(')')
        splits = splits[1].split(':')
        splits = splits[0].split(';')
        name = splits[0]
        return name

    def get_ret_type(self):
        splits = self.line[3:].split(')', 1)
        ret_type = splits[0]
        # we replace UNKNOWN_TYPE and struct by type id
        if ret_type is not type_unknown_regex().search(ret_type) and not struct_regex().search(ret_type) and not avoided_pointer_regex().search(ret_type):
            return ret_type
        return "id"

    def hook(self):
        if self.ret_type == "void":
            print '%s {[LogTool logDataFromNSString:@">>>> - %s"];%%log; %%orig;[LogTool logDataFromNSString:@"<<<< - %s"]; }' %(self.line[:-2], self.full_name, self.full_name)
        else:
            print '%s {[LogTool logDataFromNSString:@">>>> - %s"];%%log; %s ret = %%orig;[LogTool logDataFromNSString:[NSString stringWithFormat: @"<<<< - %s ==> ret value: %s", ret]];return ret; }' %(self.line[:-2], self.full_name, self.ret_type, self.full_name, map_format_specifier(self.ret_type))



class HeaderParser():
    def __init__(self, filepath):
        self.file = open(filepath)
        self.lines = self.file.readlines()
        self.interface = self.get_interface_name()
        self.methods = self.get_methods()

    def get_interface_name(self):
        for line in self.lines:
            if "@interface" in line:
                splits = line.split(' ')
                return splits[1]

    def get_methods(self):
        methods = []
        for line in self.lines:
            if "- (" == line[:3] or "+ (" == line[:3]:
                method = ObjcMethod(line, self.interface)
                methods.append(method)
        return methods

def hook_file(filepath):
    parser = HeaderParser(filepath)
    if (parser.interface == None):
        return
    print "%hook", parser.interface
    for method in parser.methods:
        if method.name not in ".cxx_destruct" and method.name not in ".cxx_construct" and not method.skip:
            method.hook()
    print "%end"

def hook_many_files(filepaths):
    for file in filepaths:
        hook_file(file)


def get_all_header_files(basepath, pattern=""):
    files = glob.glob(basepath + "*.h")
    print("// %d files found" %(len(files)))
    return files

def filter_files(files, regex_pattern):
    try:
        regex = re.compile(regex_pattern, re.IGNORECASE)
        selected_files = filter(regex.search, files)
        print("// %d filtered files" %(len(selected_files)))
        return selected_files
    except re.error:
        print("invalid regex pattern, exiting...")
        sys.exit()

def print_hookify_header():
    print("///////////////////////////////////////////////////////////////////////////\n///////////////////////////////////////////////////////////////////////////\n//////// Following hooked methods has been generated by Hookify\n//////// \n//////// Happy ~Hacking~ Security Research ;)\n///////////////////////////////////////////////////////////////////////////\n///////////////////////////////////////////////////////////////////////////\n")

def usage():
    print("usage: python hookify.py [d:p:r:f:] [dir= pattern= regex= file=]")
    print("\nto hook an entire directory based on class name pre-made regex pattern use:")
    print("\tpython hookify.py -d <your_dir_path> -p [network|crypto]")
    print("\nto hook an entire directory based on class name custom regex pattern use:")
    print("\tpython hookify.py -d <your_dir_path> -r <your_regex_string>")
    print("\nto hook a simple header file use:")
    print("\tpython hookify.py -f <your_file_path>")

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'd:p:r:f:', ['dir=', 'pattern=', 'regex=', 'file='])
    except getopt.GetoptError:
        print('unknown error with getopt')
        sys.exit()

    dumped_class_filter_pattern = None
    headers_directory_path = None
    header_file_path = None
    missing_required_option = True

    for opt, arg in opts:
        if opt in ('-p', '--pattern'):
            if arg not in ['crypto', 'network']:
                print('unkown pattern %s, did you mean: "crypto" or "network" ?' %(arg))
                usage()
                sys.exit()
            elif arg == 'network':
                dumped_class_filter_pattern = NETWORKING_CLASS_PATTERN
            elif arg == 'crypto':
                dumped_class_filter_pattern = CRYPTO_CLASS_PATTERN
        elif opt in ('-r', '--regex'):
            dumped_class_filter_pattern = arg
        elif opt in ('-d', '--dir'):
            headers_directory_path = arg
        elif opt in ('-f', '--file'):
            header_file_path = arg

    if headers_directory_path:
        print_hookify_header()
        if not dumped_class_filter_pattern:
            print("no filter pattern set for directory dump, please choose a pattern")
            usage()
            sys.exit()
        files = get_all_header_files(headers_directory_path)
        filtered_files = filter_files(files, dumped_class_filter_pattern)
        hook_many_files(filtered_files)
    elif header_file_path:
        print_hookify_header()
        hook_file(header_file_path)
    else:
        usage()
main(sys.argv)
