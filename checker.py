import os
import sys
import time
import json
import math
import msvcrt
import ctypes
import ctypes.wintypes
import subprocess


class macro_checker:
    def __init__(self):
        os.system('')
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        self.r = '\033[91m'
        self.g = '\033[92m'
        self.y = '\033[93m'
        self.c = '\033[96m'
        self.x = '\033[0m'
        self.b = '\033[1m'
        try:
            ctypes.windll.psapi.EnumProcessModules.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(ctypes.wintypes.HMODULE), ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.DWORD)]
            ctypes.windll.psapi.EnumProcessModules.restype = ctypes.wintypes.BOOL
            ctypes.windll.psapi.GetModuleFileNameExW.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.HMODULE, ctypes.wintypes.LPWSTR, ctypes.wintypes.DWORD]
            ctypes.windll.psapi.GetModuleFileNameExW.restype = ctypes.wintypes.DWORD
        except Exception:
            pass
        self.procs = [
            'autohotkey.exe', 'autohotkeyu64.exe', 'autohotkeya32.exe', 'ahk.exe',
            'tinytask.exe', 'opautoclicker.exe', 'speedautoclicker.exe', 'gsautoclicker.exe',
            'macrorecorder.exe', 'jitbit.exe', 'tgmacro.exe', 'autoit3.exe', 'autoit.exe',
            'pulover.exe', 'xmousebuttoncontrol.exe', 'keyremapper.exe', 'autotyper.exe',
            'fastkeys.exe', 'chatpacker.exe', 'spambot.exe', 'macrotoolworks.exe'
        ]
        self.kw = [
            'pyautogui', 'pynput', 'keyboard', 'typewrite', 'sendkeys', 'discord_pack',
            'chat_pack', 'ladder', 'robotjs', 'nut-js', 'autotype', 'spambot', 'packbot'
        ]
        self.dirs = [
            os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Recent'),
            r'C:\Windows\Prefetch',
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~/Desktop'),
            os.path.expandvars(r'%TEMP%')
        ]

    def cls(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def banner(self):
        b = r'''
  __  __    _    ____ ____   ___     ____ _   _ _____ ____ _  _______ ____  
 |  \/  |  / \  / ___|  _ \ / _ \   / ___| | | | ____/ ___| |/ / ____|  _ \ 
 | |\/| | / _ \| |   | |_) | | | | | |   | |_| |  _|| |   | ' /|  _| | |_) |
 | |  | |/ ___ \ |___|  _ <| |_| | | |___|  _  | |__| |___| . \| |___|  _ < 
 |_|  |_/_/   \_\____|_| \_\\___/   \____|_| |_|_____|____|_|\_\_____|_| \_\
'''
        print(f'{self.c}{b}{self.x}')
        print(f'{self.c}pack checker // anti macro discord{self.x}\n')

    def get_procs(self):
        res = []
        try:
            cmd = ['powershell', '-NoProfile', '-Command', 'Get-CimInstance Win32_Process | Select-Object ProcessId, Name, CommandLine, ExecutablePath | ConvertTo-Json -Compress']
            out = subprocess.run(cmd, capture_output=True, text=True, errors='ignore').stdout.strip()
            if out:
                d = json.loads(out)
                if isinstance(d, dict):
                    d = [d]
                for i in d:
                    res.append({'pid': i.get('ProcessId', 0), 'name': (i.get('Name') or '').lower(), 'cmd': i.get('CommandLine') or '', 'path': i.get('ExecutablePath') or ''})
        except Exception:
            pass
        if not res:
            try:
                out = subprocess.run(['tasklist', '/fo', 'csv'], capture_output=True, text=True, errors='ignore').stdout
                for ln in out.splitlines()[1:]:
                    pts = [x.strip(' "') for x in ln.split('","')]
                    if len(pts) >= 2:
                        res.append({'pid': int(pts[1]) if pts[1].isdigit() else 0, 'name': pts[0].lower(), 'cmd': '', 'path': ''})
            except Exception:
                pass
        return res

    def get_dlls(self, pid):
        dlls = []
        try:
            h = ctypes.windll.kernel32.OpenProcess(0x0410, False, pid)
            if not h:
                return dlls
            mods = (ctypes.wintypes.HMODULE * 512)()
            cb = ctypes.wintypes.DWORD()
            if ctypes.windll.psapi.EnumProcessModules(h, mods, ctypes.sizeof(mods), ctypes.byref(cb)):
                cnt = int(cb.value // ctypes.sizeof(ctypes.wintypes.HMODULE))
                for i in range(cnt):
                    buf = ctypes.create_unicode_buffer(512)
                    if ctypes.windll.psapi.GetModuleFileNameExW(h, mods[i], buf, 512):
                        dlls.append(buf.value)
            ctypes.windll.kernel32.CloseHandle(h)
        except Exception:
            pass
        return dlls

    def check_file(self, fp):
        hits = []
        if not fp or not os.path.isfile(fp):
            return hits
        try:
            with open(fp, 'r', errors='ignore') as f:
                s = f.read(32768).lower()
                for k in self.kw:
                    if k in s:
                        hits.append(k)
        except Exception:
            pass
        return hits

    def check_exe(self, fp):
        if not fp:
            return []
        flow = fp.lower()
        if flow.startswith(('c:\\windows\\system32', 'c:\\windows\\winsxs', 'c:\\program files\\windowsapps')):
            return []
        hits = []
        try:
            if not os.path.isfile(fp):
                return hits
            sz = os.path.getsize(fp)
            with open(fp, 'rb') as f:
                b = f.read(524288)
                if sz > 524288:
                    f.seek(max(0, sz - 524288))
                    b += f.read()
                blow = b.lower()
                is_py = False
                if b'pyinstaller' in blow or b'_meipass2' in blow or b'pyz-00.pyz' in blow:
                    hits.append('python facut in exe (pyinstaller)')
                    is_py = True
                elif b'nuitka' in blow:
                    hits.append('python facut in exe (nuitka)')
                    is_py = True
                elif b'py2exe' in blow:
                    hits.append('python facut in exe (py2exe)')
                    is_py = True
                elif b'cx_freeze' in blow:
                    hits.append('python facut in exe (cx_freeze)')
                    is_py = True
                for k in (b'pyautogui', b'pynput', b'autohotkey', b'robotjs', b'tinytask'):
                    if k in blow:
                        hits.append(f'librarie in exe: {k.decode()}')
                if is_py and b'keyboard' in blow:
                    hits.append('librarie in exe: keyboard')
        except Exception:
            pass
        return hits

    def scan_procs(self):
        print(f'{self.y}> scanare procese pornite...{self.x}\n')
        ps = self.get_procs()
        cnt = 0
        for p in ps:
            nm = p['name']
            cmd = p['cmd']
            pid = p['pid']
            pth = p['path']
            reasons = []
            if nm in self.procs:
                reasons.append(f'macro: {nm}')
            elif nm in ('python.exe', 'pythonw.exe'):
                clow = cmd.lower()
                for k in self.kw:
                    if k in clow:
                        reasons.append(f'argument: {k}')
                for tok in cmd.split():
                    c_tok = tok.strip('\'"')
                    if c_tok.endswith('.py') and os.path.isfile(c_tok):
                        fhits = self.check_file(c_tok)
                        fn_only = os.path.basename(c_tok)
                        reasons.append(f'{fn_only} ({", ".join(fhits)})' if fhits else fn_only)
            elif nm == 'node.exe':
                clow = cmd.lower()
                for k in ('robotjs', 'nut-js', 'sendkeys', 'pack', 'spam', 'ladder', 'macro'):
                    if k in clow:
                        reasons.append(f'argument node: {k}')
                for tok in cmd.split():
                    c_tok = tok.strip('\'"')
                    if c_tok.endswith('.js') and os.path.isfile(c_tok):
                        fhits = self.check_file(c_tok)
                        fn_only = os.path.basename(c_tok)
                        reasons.append(f'{fn_only} ({", ".join(fhits)})' if fhits else fn_only)
            elif nm in ('cmd.exe', 'powershell.exe'):
                clow = cmd.lower()
                for k in ('sendkeys', 'autohotkey', '.ahk'):
                    if k in clow:
                        reasons.append(f'comanda: {k}')
            else:
                dlls = self.get_dlls(pid)
                py_dlls = [d for d in dlls if any(x in d.lower() for x in ('python3', '_mei', 'pyinstaller', 'pyarmor', 'nuitka'))]
                if py_dlls:
                    reasons.append(f'python facut in exe (dll: {os.path.basename(py_dlls[0])})')
                mc_dlls = [d for d in dlls if any(x in os.path.basename(d).lower() for x in ('pyautogui', 'pynput', 'robotjs', 'autohotkey', '_winkeyboard'))]
                if mc_dlls:
                    reasons.append(f'modul incarcat: {os.path.basename(mc_dlls[0])}')
                if pth and os.path.isfile(pth):
                    exe_hits = self.check_exe(pth)
                    if exe_hits:
                        reasons.extend(exe_hits)
            if reasons:
                cnt += 1
                full_pth = cmd if (pth and pth in cmd) else (f'{pth}  {cmd}'.strip() if (pth and cmd) else (pth or cmd))
                print(f'{self.r}🚨 SCLAVOI GASIT:{self.x}')
                print(f'pid: {pid}')
                print(f'app: {nm}')
                print(f'details -> {"; ".join(reasons)}')
                print(f'path:  {full_pth}\n')
        if cnt == 0:
            print(f'{self.g}> nu ruleaza niciun macro acum.{self.x}\n')
        else:
            print(f'{self.r}> total procese macro gasite: {cnt}{self.x}\n')
        return cnt

    def scan_recent(self):
        print(f'{self.y}> verificare fisiere si aplicatii deschise in ultima ora...{self.x}\n')
        now = time.time()
        sus_cnt = 0
        tot_cnt = 0
        for d in self.dirs:
            if not os.path.exists(d):
                continue
            try:
                fns = os.listdir(d)
            except Exception:
                continue
            d_sus = []
            d_all = []
            for fn in fns:
                fp = os.path.join(d, fn)
                try:
                    mt = os.path.getmtime(fp)
                    diff = now - mt
                    if 0 <= diff <= 3600:
                        tot_cnt += 1
                        m = int(diff // 60)
                        s = int(diff % 60)
                        ago = f'acum {m}m {s}s'
                        flow = fn.lower()
                        is_sus = False
                        det = ago
                        if flow.endswith('.pf'):
                            exe = flow.split('-')[0]
                            if exe in self.procs or exe in ('python.exe', 'node.exe', 'cmd.exe', 'powershell.exe'):
                                is_sus = True
                                det = f'prefetch ({exe}) {ago}'
                        elif flow.endswith('.exe'):
                            ehits = self.check_exe(fp)
                            if ehits:
                                is_sus = True
                                det = f'{", ".join(ehits)} ({ago})'
                        for k in self.kw:
                            if k in flow:
                                is_sus = True
                                det = f'cuvant cheie: {k} ({ago})'
                        if any(flow.endswith(ext) for ext in ('.ahk', '.ahk.lnk', '.py', '.py.lnk', '.js', '.js.lnk', '.bat', '.ps1')):
                            is_sus = True
                            det = f'script gasit ({ago})'
                        if is_sus:
                            d_sus.append({'fn': fn, 'fp': fp, 'det': det})
                            sus_cnt += 1
                        else:
                            d_all.append(f'{fn} ({ago})')
                except Exception:
                    pass
            if d_sus or d_all:
                print(f'{self.c}> folder: {d}{self.x}')
                for item in d_sus:
                    print(f'{self.r}🚨 SCLAVOI GASIT:{self.x}')
                    print('pid: n/a (recent)')
                    print(f'app: {item["fn"]}')
                    print(f'details -> {item["det"]}')
                    print(f'path:  {item["fp"]}\n')
                for item in d_all[:6]:
                    print(f'  deschis: {item}')
                if len(d_all) > 6:
                    print(f'  si inca {len(d_all) - 6} fisiere')
                print('')
        if sus_cnt == 0:
            print(f'{self.g}> nu a deschis nimic suspect in ultima ora.{self.x}')
            print(f'{self.g}  total fisiere accesate: {tot_cnt}{self.x}\n')
        else:
            print(f'{self.r}> gasite {sus_cnt} fisiere suspecte deschise recent (total: {tot_cnt}){self.x}\n')
        return sus_cnt

    def ladder_test(self):
        print(f'{self.y}> test viteza si ladder typing{self.x}')
        print('scrie sau baga textul aici, enter dupa fiecare linie.')
        print('cand termini scrie /done pe linie noua sau apasa esc.\n')
        char_dts = []
        line_dts = []
        lines = []
        cur_ln = []
        last_c = None
        last_l = None
        t0 = None
        while True:
            try:
                ch = msvcrt.getwch()
            except Exception:
                break
            now = time.perf_counter()
            if t0 is None:
                t0 = now
                last_l = now
            if ch == '\x1b':
                break
            if ch == '\r':
                sys.stdout.write('\n')
                sys.stdout.flush()
                ln_str = ''.join(cur_ln)
                if ln_str.strip() == '/done':
                    break
                lines.append(ln_str)
                if last_l is not None:
                    line_dts.append(now - last_l)
                last_l = now
                cur_ln = []
                continue
            if ch == '\x08':
                if cur_ln:
                    cur_ln.pop()
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
                continue
            sys.stdout.write(ch)
            sys.stdout.flush()
            cur_ln.append(ch)
            if last_c is not None:
                char_dts.append((now - last_c) * 1000)
            last_c = now
        t1 = time.perf_counter()
        dur = (t1 - t0) if t0 else 0
        tot_c = sum(len(l) for l in lines) + len(cur_ln)
        tot_l = len(lines)
        if tot_l == 0 and tot_c == 0:
            print(f'\n{self.y}> nu ai scris nimic.{self.x}\n')
            return
        wpm = (tot_c / 5) / (dur / 60) if dur > 0 else 0
        avg_c = sum(char_dts) / len(char_dts) if char_dts else 0
        sd_c = (sum((x - avg_c) ** 2 for x in char_dts) / len(char_dts)) ** 0.5 if char_dts else 0
        avg_l = (sum(line_dts) / len(line_dts)) * 1000 if line_dts else 0
        min_l = min(line_dts) * 1000 if line_dts else 0
        flags = []
        if wpm > 230:
            flags.append(f'scrie prea rapid ({wpm:.1f} wpm, omul nu trece de 200)')
        if avg_c < 25 and len(char_dts) >= 10:
            flags.append(f'tasteaza instant ({avg_c:.1f}ms intre taste, e autotyper)')
        if sd_c < 3.0 and len(char_dts) >= 15:
            flags.append(f'delay identic intre taste (deviatie {sd_c:.2f}ms, tastat mecanic)')
        if tot_l >= 3 and avg_l < 150:
            flags.append(f'ladder macro ({avg_l:.0f}ms intre linii, spam automat de pack)')
        if tot_l >= 2 and min_l < 40:
            flags.append(f'paste sau burst ({min_l:.0f}ms intre linii)')
        print(f'\n{self.c}> rezultate test:{self.x}')
        print(f'  linii: {tot_l}')
        print(f'  caractere: {tot_c}')
        print(f'  secunde: {dur:.2f}s')
        print(f'  wpm: {wpm:.1f}')
        print(f'  ms intre taste: {avg_c:.1f}ms')
        print(f'  variatie taste: {sd_c:.2f}ms')
        print(f'  ms intre linii: {avg_l:.1f}ms')
        print(f'  minim intre linii: {min_l:.1f}ms')
        if flags:
            print(f'\n{self.r}🚨 SCLAVOI GASIT:{self.x}')
            print('pid: n/a (live input)')
            print('app: discord packing macro')
            print(f'details -> {"; ".join(flags)}')
            print('path:  consola live\n')
        else:
            print(f'\n{self.g}> e curat, scrie de mana.{self.x}\n')

    def full_scan(self):
        print(f'{self.c}> verificare completa pc...{self.x}\n')
        p_hits = self.scan_procs()
        r_hits = self.scan_recent()
        print(f'{self.c}> rezumat:{self.x}')
        print(f'  procese macro pornite: {p_hits}')
        print(f'  fisiere recente suspecte: {r_hits}\n')
        ans = input(f'{self.y}> vrei sa bagi si testul de ladder acum? (y/n): {self.x}').strip().lower()
        if ans == 'y':
            self.ladder_test()

    def menu(self):
        while True:
            self.banner()
            print('1. scan procese (ahk, python, node, autotypere)')
            print('2. fisiere deschise in ultima ora')
            print('3. test ladder typing / viteza')
            print('4. check complet')
            print('5. iesire\n')
            c = input(f'{self.y}> alege (1-5): {self.x}').strip()
            print('')
            if c == '1':
                self.scan_procs()
            elif c == '2':
                self.scan_recent()
            elif c == '3':
                self.ladder_test()
            elif c == '4':
                self.full_scan()
            elif c == '5':
                print(f'{self.c}iesire.{self.x}')
                break
            else:
                print(f'{self.r}optiune invalida.{self.x}\n')
            input(f'{self.b}apasa enter sa continui...{self.x}')
            self.cls()


def main():
    chk = macro_checker()
    chk.cls()
    chk.menu()


if __name__ == '__main__':
    main()
