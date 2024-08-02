#!/usr/bin/python3

def main():
    print('Content-Type: text/plain')
    print('Set-Cookie: foo=bar; domain=bar.com; path=/cgi-bin/')
    print()
    print('hello world')
    

if __name__ == '__main__':
    main()
