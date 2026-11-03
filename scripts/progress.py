#!/usr/bin/env python3
"""Branded, zero-dependency progress renderer used during real installation."""
import argparse
import os
import shutil

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('step',type=int)
    ap.add_argument('label')
    args=ap.parse_args()
    n=max(0,min(6,args.step))
    columns=shutil.get_terminal_size((80,25)).columns
    count=24 if columns>=75 else 14
    done=round(count*n/6)
    bar='━'*done+'·'*(count-done)
    # Each completed step reflects a real completed installer stage, not a timer.
    print(f'  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓') if columns>=76 else None
    print(f'  ✳ KUHL / INSTALL     [{bar}] {n*100//6:>3}%')
    print(f'    {args.label}')
    if columns>=76:print('  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛')
    print('')
if __name__=='__main__':main()
