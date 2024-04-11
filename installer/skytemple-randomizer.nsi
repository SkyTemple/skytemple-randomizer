!include LogicLib.nsh

;;; UNINSTALL LOG MACRO:
;;; https://nsis.sourceforge.io/Uninstall_only_installed_files
;AddItem macro
  !macro AddItem Path
    FileWrite $UninstLog "${Path}$\r$\n"
  !macroend

;File macro
  !macro File FileName
     IfFileExists "$OUTDIR\${FileName}" +2
     FileWrite $UninstLog "$OUTDIR\${FileName}$\r$\n"
     File "${FileName}"
  !macroend

;CreateShortCut macro
  !macro CreateShortCut FilePath FilePointer Pamameters Icon IconIndex
    FileWrite $UninstLog "${FilePath}$\r$\n"
    CreateShortCut "${FilePath}" "${FilePointer}" "${Pamameters}" "${Icon}" "${IconIndex}"
  !macroend

;Copy files macro
  !macro CopyFiles SourcePath DestPath
    IfFileExists "${DestPath}" +2
    FileWrite $UninstLog "${DestPath}$\r$\n"
    CopyFiles "${SourcePath}" "${DestPath}"
  !macroend

;Rename macro
  !macro Rename SourcePath DestPath
    IfFileExists "${DestPath}" +2
    FileWrite $UninstLog "${DestPath}$\r$\n"
    Rename "${SourcePath}" "${DestPath}"
  !macroend

;CreateDirectory macro
  !macro CreateDirectory Path
    CreateDirectory "${Path}"
    FileWrite $UninstLog "${Path}$\r$\n"
  !macroend

;SetOutPath macro
  !macro SetOutPath Path
    SetOutPath "${Path}"
    FileWrite $UninstLog "${Path}$\r$\n"
  !macroend

;WriteUninstaller macro
  !macro WriteUninstaller Path
    WriteUninstaller "${Path}"
    FileWrite $UninstLog "${Path}$\r$\n"
  !macroend

;WriteIniStr macro
  !macro WriteIniStr IniFile SectionName EntryName NewValue
     IfFileExists "${IniFile}" +2
     FileWrite $UninstLog "${IniFile}$\r$\n"
     WriteIniStr "${IniFile}" "${SectionName}" "${EntryName}" "${NewValue}"
  !macroend

;WriteRegStr macro
  !macro WriteRegStr RegRoot UnInstallPath Key Value
     FileWrite $UninstLog "${RegRoot} ${UnInstallPath}$\r$\n"
     WriteRegStr "${RegRoot}" "${UnInstallPath}" "${Key}" "${Value}"
  !macroend


;WriteRegDWORD macro
  !macro WriteRegDWORD RegRoot UnInstallPath Key Value
     FileWrite $UninstLog "${RegRoot} ${UnInstallPath}$\r$\n"
     WriteRegDWORD "${RegRoot}" "${UnInstallPath}" "${Key}" "${Value}"
  !macroend

;BackupFile macro
  !macro BackupFile FILE_DIR FILE BACKUP_TO
   IfFileExists "${BACKUP_TO}\*.*" +2
    CreateDirectory "${BACKUP_TO}"
   IfFileExists "${FILE_DIR}\${FILE}" 0 +2
    Rename "${FILE_DIR}\${FILE}" "${BACKUP_TO}\${FILE}"
  !macroend

;RestoreFile macro
  !macro RestoreFile BUP_DIR FILE RESTORE_TO
   IfFileExists "${BUP_DIR}\${FILE}" 0 +2
    Rename "${BUP_DIR}\${FILE}" "${RESTORE_TO}\${FILE}"
  !macroend

;BackupFiles macro
  !macro BackupFiles FILE_DIR FILE BACKUP_TO
   IfFileExists "${BACKUP_TO}\*.*" +2
    CreateDirectory "22222"
   IfFileExists "${FILE_DIR}\${FILE}" 0 +7
    FileWrite $UninstLog "${FILE_DIR}\${FILE}$\r$\n"
    FileWrite $UninstLog "${BACKUP_TO}\${FILE}$\r$\n"
    FileWrite $UninstLog "FileBackup$\r$\n"
    Rename "${FILE_DIR}\${FILE}" "${BACKUP_TO}\${FILE}"
    SetOutPath "${FILE_DIR}"
    File "${FILE}" #After the Original file is backed up write the new file.
  !macroend

;RestoreFiles macro
  !macro RestoreFiles BUP_FILE RESTORE_FILE
   IfFileExists "${BUP_FILE}" 0 +2
    CopyFiles "${BUP_FILE}" "${RESTORE_FILE}"
  !macroend
;;;
;;; END UNINSTALL MACRO

Function UninstallPrevious
    ; Check for uninstaller.
    ReadRegStr $R0 HKLM "${HKLM_REG_KEY}" "InstallDir"

    ${If} $R0 == ""
        Goto Done
    ${EndIf}

    DetailPrint "Removing previous installation."

    ; Run the uninstaller silently.
    ExecWait '"$R0\Uninstall.exe /S"'

    Done:
FunctionEnd

!define PRODUCT_NAME "SkyTemple Randomizer"

!define DIST_DIR "dist\skytemple_randomizer"
!define APPEXE "skytemple_randomizer.exe"
!define PRODUCT_ICON "skytemple_randomizer.ico"

SetCompressor lzma

RequestExecutionLevel admin

; Modern UI
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"

; UI pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "Spanish"
!insertmacro MUI_LANGUAGE "Japanese"
; Modern UI end

Name "${PRODUCT_NAME} - ${PRODUCT_VERSION}"
Icon "skytemple_randomizer.ico"
OutFile "skytemple-randomizer-${PRODUCT_VERSION}-x64-install.exe"
InstallDir "$PROGRAMFILES64\${PRODUCT_NAME}"
ShowInstDetails show

;;; UNINSTALL LOG SUPPORT
;;; https://nsis.sourceforge.io/Uninstall_only_installed_files
;--------------------------------
; Configure UnInstall log to only remove what is installed
;--------------------------------
;Set the name of the uninstall log
!define UninstLog "uninstall.log"
Var UninstLog
;The root registry to write to
!define REG_ROOT "HKLM"
;The registry path to write to
!define REG_APP_PATH "SOFTWARE\appname"

;Uninstall log file missing.
LangString UninstLogMissing ${LANG_ENGLISH} "${UninstLog} not found!$\r$\nUninstallation cannot proceed!"

;AddItem macro
!define AddItem "!insertmacro AddItem"

;BackupFile macro
!define BackupFile "!insertmacro BackupFile"

;BackupFiles macro
!define BackupFiles "!insertmacro BackupFiles"

;Copy files macro
!define CopyFiles "!insertmacro CopyFiles"

;CreateDirectory macro
!define CreateDirectory "!insertmacro CreateDirectory"

;CreateShortcut macro
!define CreateShortcut "!insertmacro CreateShortcut"

;File macro
!define File "!insertmacro File"

;Rename macro
!define Rename "!insertmacro Rename"

;RestoreFile macro
!define RestoreFile "!insertmacro RestoreFile"

;RestoreFiles macro
!define RestoreFiles "!insertmacro RestoreFiles"

;SetOutPath macro
!define SetOutPath "!insertmacro SetOutPath"

;WriteRegDWORD macro
!define WriteRegDWORD "!insertmacro WriteRegDWORD"

;WriteRegStr macro
!define WriteRegStr "!insertmacro WriteRegStr"

;WriteUninstaller macro
!define WriteUninstaller "!insertmacro WriteUninstaller"

Section -openlogfile
CreateDirectory "$INSTDIR"
IfFileExists "$INSTDIR\${UninstLog}" +3
  FileOpen $UninstLog "$INSTDIR\${UninstLog}" w
Goto +4
  SetFileAttributes "$INSTDIR\${UninstLog}" NORMAL
  FileOpen $UninstLog "$INSTDIR\${UninstLog}" a
  FileSeek $UninstLog 0 END
SectionEnd
;;;
;;; END UNINSTALL LOG SUPPORT

Section "" SecUninstallPrevious

    Call UninstallPrevious

SectionEnd

Section "install"
  ${SetOutPath} $INSTDIR
  ${File} /r "${DIST_DIR}\*"
  ${File} ${PRODUCT_ICON}

  ${CreateShortCut} "$SMPROGRAMS\${PRODUCT_NAME}.lnk" "$INSTDIR\${APPEXE}" "" "$INSTDIR\${PRODUCT_ICON}"
  ${WriteUninstaller} $INSTDIR\uninstall.exe
  ; Add ourselves to Add/remove programs
  ${WriteRegStr} HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "DisplayName" "${PRODUCT_NAME}"
  ${WriteRegStr} HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "UninstallString" '"$INSTDIR\uninstall.exe"'
  ${WriteRegStr} HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "InstallLocation" "$INSTDIR"
  ${WriteRegStr} HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "DisplayIcon" "$INSTDIR\${PRODUCT_ICON}"
  ${WriteRegDWORD} HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "NoModify" 1
  ${WriteRegDWORD} HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "NoRepair" 1
SectionEnd

;--------------------------------
; Uninstaller
;--------------------------------
Section Uninstall
  ;Can't uninstall if uninstall log is missing!
  IfFileExists "$INSTDIR\${UninstLog}" +3
    MessageBox MB_OK|MB_ICONSTOP "$(UninstLogMissing)"
      Abort

  Push $R0
  Push $R1
  Push $R2
  SetFileAttributes "$INSTDIR\${UninstLog}" NORMAL
  FileOpen $UninstLog "$INSTDIR\${UninstLog}" r
  StrCpy $R1 -1

  GetLineCount:
    ClearErrors
    FileRead $UninstLog $R0
    IntOp $R1 $R1 + 1
    StrCpy $R0 $R0 -2
    Push $R0
    IfErrors 0 GetLineCount

  Pop $R0

  LoopRead:
    StrCmp $R1 0 LoopDone
    Pop $R0

    IfFileExists "$R0\*.*" 0 +3
      RMDir $R0  #is dir
    Goto +9
    IfFileExists $R0 0 +3
      Delete $R0 #is file
    Goto +6
    StrCmp $R0 "${REG_ROOT} ${REG_APP_PATH}" 0 +3
      DeleteRegKey ${REG_ROOT} "${REG_APP_PATH}" #is Reg Element
    Goto +3
    StrCmp $R0 "${REG_ROOT} ${UNINSTALL_PATH}" 0 +2
      DeleteRegKey ${REG_ROOT} "${UNINSTALL_PATH}" #is Reg Element

    IntOp $R1 $R1 - 1
    Goto LoopRead
  LoopDone:
  FileClose $UninstLog
  Delete "$INSTDIR\${UninstLog}"
  RMDir "$INSTDIR"
  Pop $R2
  Pop $R1
  Pop $R0

  ;Remove registry keys
    ;DeleteRegKey ${REG_ROOT} "${REG_APP_PATH}"
    ;DeleteRegKey ${REG_ROOT} "${UNINSTALL_PATH}"
SectionEnd
