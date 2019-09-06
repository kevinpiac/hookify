import re

# Following patterns are used to filter hooked Classes by name
# TODO: add more patterns later
NETWORKING_CLASS_PATTERN = r"(api)|(request)|(http)|(client)|(auth)|(socket)|(protobuf)|(URL)|(GPB)|(Networking)|(SOAP)"
CRYPTO_CLASS_PATTERN = r"(AES)|(HMAC)|(RSA)|(Hash)|(SSL)|(Enigma)|(Cryptor)|(JOSE)|(JWE)|(JWK)|(cipher)|(Elliptic)|(Curve)|(NSData-)|(crypto)|(encrypt)|(decrypt)|(encod)|(decod)|(security)|(secure)|(guard)|(auth)|(jailbreak)|(obfuscation)|(token)|(keychain)"
# ANY_CLASSE_PATTERN = r".*" not used


# Following patterns are use to replace returned types and argument types
# to avoid compiler crashing

STRUCT_PATTERN = r"((struct )[a-z-0-9_ *]*)|(CDStruct_[a-z-0-9]* *)"
# MATCHES FOLLOWING PATTERNS
#
# struct NetworkApi;
# struct NetworkDelegate;
# struct NetworkManager;
# struct __NetworkManagerNotifier;
# struct __NetworkTrafficAnnotationTag
# struct _NSZone *
# struct NSZone *
# struct sqlite3 *
# struct Nonce
# struct NumberResponder;
# struct OCSPVerifyResult
# CDStruct_bac8f6e9
# CDStruct_e83c9415

AVOIDED_POINTER_PATTERN = r"((const) (shared|function)[a-z_0-9 *]* *)"
# MATCHES FOLLOWING PATTERNS
#
# const shared_ptr_7dd28b8f *
# const function_1dcf92b8

TYPE_POINTER_PATTERN = r"(([a-z]* ){1,3}\*)"
# MATCHES FOLLOWING PATTERNS
#
# unsigned long long *
# unsigned long *
# char *
# void *

TYPE_UNKNOWN_PATTERN = r"(CDUnknown[a-z]*)|(scoped[_a-z-0-9]*)|(CDUnion_[a-z-0-9 \*]*)"
# MATCHES FOLLOWING PATTERNS
#
# CDUnknownBlockType
# CDUnknownFunctionPointerType
# CDUnion_88782d86 *
# scoped_refptr_81e0d7bb << known as <dependent types>
# scoped_refptr_2ke0cedb << known as <dependent types>


def struct_regex():
    return re.compile(STRUCT_PATTERN, re.IGNORECASE)

def files_of_interest_regex():
    return re.compile(FILES_OF_INTEREST_PATTERN, re.IGNORECASE)

def avoided_pointer_regex():
    return re.compile(AVOIDED_POINTER_PATTERN, re.IGNORECASE)

def type_pointer_regex():
    return re.compile(TYPE_POINTER_PATTERN, re.IGNORECASE)

def type_unknown_regex():
    return re.compile(TYPE_UNKNOWN_PATTERN, re.IGNORECASE)
