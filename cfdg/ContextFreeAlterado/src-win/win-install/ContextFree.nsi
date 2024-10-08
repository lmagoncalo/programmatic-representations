; Context Free
; ---------------------
; Copyright (C) 2005 John Horigan
;
; This program is free software; you can redistribute it and/or
; modify it under the terms of the GNU General Public License
; as published by the Free Software Foundation; either version 2
; of the License, or (at your option) any later version.
;
; This program is distributed in the hope that it will be useful,
; but WITHOUT ANY WARRANTY; without even the implied warranty of
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
; GNU General Public License for more details.
;
; You should have received a copy of the GNU General Public License
; along with this program; if not, write to the Free Software
; Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
; 
; John Horigan can be contacted at john@glyphic.com or at
; John Horigan, 1209 Villa St., Mountain View, CA 94041-1123, USA
;

!define VER_MAJOR 2
!define VER_MINOR 22

SetCompressor lzma

!define PRODUCT "ContextFree"
!define VERSION "${VER_MAJOR}.${VER_MINOR}"

!include "MUI.nsh"
!include WordFunc.nsh
!insertmacro VersionCompare

;--------------------------------
;Variables

  Var MUI_TEMP
  Var STARTMENU_FOLDER
  
;--------------------------------
;Configuration

  !define MUI_ICON "ContextFree.ico"
  !define MUI_UNICON "ContextFree.ico"
  
  !define MUI_WELCOMEFINISHPAGE_BITMAP "sidebar.bmp"
  !define MUI_UNWELCOMEFINISHPAGE_BITMAP "sidebar.bmp"


  !define MUI_WELCOMEPAGE_TITLE "Context Free"
    
  
  !define MUI_FINISHPAGE_NOAUTOCLOSE
  !define MUI_UNFINISHPAGE_NOAUTOCLOSE

ShowInstDetails show
ShowUninstDetails show

  
;General
  OutFile "ContextFreeInstall.exe"
  
  ;License page
  LicenseData "license.txt"

  ;Folder-selection page
  InstallDir "$PROGRAMFILES\OzoneSoft\${PRODUCT}"
  
  Name "${PRODUCT}"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY

  ;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU" 
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\OzoneSoft\ContextFree" 
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
  
  !insertmacro MUI_PAGE_STARTMENU Application $STARTMENU_FOLDER

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

  ;Language
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Context Free (required)" 
SectionIn RO
  SetOutPath "$INSTDIR"
  ClearErrors
  
  Delete '$INSTDIR\msvcp80.dll'
  Delete '$INSTDIR\msvcr80.dll'
  Delete '$INSTDIR\mfc80.dll'
  Delete '$INSTDIR\mfc80u.dll'
  RMDir /r "$INSTDIR\Microsoft.VC80.CRT"
  RMDir /r "$INSTDIR\Microsoft.VC80.MFC"
  DeleteRegKey HKCR ".cfdg"
  DeleteRegKey HKCR "ContextFree.Document"
  
  File 'license.txt'

  File "..\\..\\src-net\\release\\ContextFree.exe" 
  File "..\\..\\src-net\\release\\CFControls.dll" 
  File "..\\..\\src-net\\release\\Controls.dll" 
  File "..\\..\\src-net\\release\\FileDlgExtenders.dll" 
  File "..\\..\\src-net\\release\\WeifenLuo.WinFormsUI.Docking.dll" 
 
  DetailPrint "Installing Visual Studio 2005 SP1 runtime libraries..."
  File "vcredist_x86.exe"
  ExecWait '"$INSTDIR\vcredist_x86.exe"'
  Delete $INSTDIR\vcredist_x86.exe

SectionEnd


Section -post

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\{DD0B06AD-5E55-41be-88E5-E9D13BAF06F4}" \
                   "DisplayName" "Context Free"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\{DD0B06AD-5E55-41be-88E5-E9D13BAF06F4}" \
                   "UninstallString" '"$INSTDIR\uninst-contextfree.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\{DD0B06AD-5E55-41be-88E5-E9D13BAF06F4}" \
                   "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\{DD0B06AD-5E55-41be-88E5-E9D13BAF06F4}" \
                   "NoRepair" 1

  SetOutPath $INSTDIR



  ; since the installer is now created last (in 1.2+), this makes sure 
  ; that any old installer that is readonly is overwritten.
  Delete $INSTDIR\uninst-contextfree.exe 
  WriteUninstaller $INSTDIR\uninst-contextfree.exe

  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    
    ;Create shortcuts
    CreateDirectory "$SMPROGRAMS\$STARTMENU_FOLDER"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\Context Free.lnk" "$INSTDIR\ContextFree.exe"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\Uninstall Context Free.lnk" "$INSTDIR\uninst-contextfree.exe"
  
  !insertmacro MUI_STARTMENU_WRITE_END

SectionEnd

Function .onInstSuccess
  Exec '"$INSTDIR\ContextFree.exe"'
FunctionEnd

Function .onInit
  Call GetDotNETVersion
  Pop $0
  ${If} $0 == "not found"
    MessageBox MB_OK|MB_ICONSTOP ".NET runtime library is not installed. Please Windows Update to install .Net runtime (version 2 or later)."
    Abort
  ${EndIf}
 
  StrCpy $0 $0 "" 1 # skip "v"
 
  ${VersionCompare} $0 "2.0" $1
  ${If} $1 == 2
    MessageBox MB_OK|MB_ICONSTOP ".NET runtime library v2.0 or newer is required. You have $0.  Please Windows Update to install v2.0 (or later)."
    Abort
  ${EndIf}

  SetOutPath $TEMP
  File /oname=spltmp.bmp "splash.bmp"

  splash::show 4000 $TEMP\spltmp
  
  Pop $0 ; $0 has '1' if the user closed the splash screen early,
         ; '0' if everything closed normal, and '-1' if some error occured.

  Delete $TEMP\spltmp.bmp
FunctionEnd

Function GetDotNETVersion
  Push $0
  Push $1
 
  System::Call "mscoree::GetCORVersion(w .r0, i ${NSIS_MAX_STRLEN}, *i) i .r1 ?u"
  StrCmp $1 "error" 0 +2
    StrCpy $0 "not found"
 
  Pop $1
  Exch $0
FunctionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"
  IfFileExists $INSTDIR\ContextFree.exe skip_confirmation
    MessageBox MB_YESNO "It does not appear that Context Free is installed.$\r$\nContinue anyway (not recommended)" IDYES skip_confirmation
    Abort "Uninstall aborted by user."
  skip_confirmation:

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\{DD0B06AD-5E55-41be-88E5-E9D13BAF06F4}"

  Delete '$INSTDIR\ContextFree.exe'
  Delete '$INSTDIR\CFControls.dll' 
  Delete '$INSTDIR\Controls.dll'
  Delete '$INSTDIR\FileDlgExtenders.dll'
  Delete '$INSTDIR\WeifenLuo.WinFormsUI.Docking.dll'
  Delete '$INSTDIR\license.txt'
  Delete '$INSTDIR\uninst-contextfree.exe' 
  RMDir  '$INSTDIR'
  RMDir  "$PROGRAMFILES\OzoneSoft"

  !insertmacro MUI_STARTMENU_GETFOLDER Application $MUI_TEMP
    
  Delete "$SMPROGRAMS\$MUI_TEMP\Uninstall Context Free.lnk"
  Delete "$SMPROGRAMS\$MUI_TEMP\Context Free.lnk"
  
  ;Delete empty start menu parent diretories
  StrCpy $MUI_TEMP "$SMPROGRAMS\$MUI_TEMP"
 
  startMenuDeleteLoop:
	ClearErrors
    RMDir $MUI_TEMP
    GetFullPathName $MUI_TEMP "$MUI_TEMP\.."
    
    IfErrors startMenuDeleteLoopDone
  
    StrCmp $MUI_TEMP $SMPROGRAMS startMenuDeleteLoopDone startMenuDeleteLoop
  startMenuDeleteLoopDone:

  DeleteRegKey HKCU "SOFTWARE\OzoneSoft\ContextFree" 
  DeleteRegKey HKCR ".cfdg"
  DeleteRegKey HKCR "ContextFree.Document"


SectionEnd

;eof
