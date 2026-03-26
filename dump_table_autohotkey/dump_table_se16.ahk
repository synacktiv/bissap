#Requires AutoHotkey v2.0
#SingleInstance Force

CoordMode "Pixel", "Screen"
CoordMode "Mouse", "Screen"

DefaultTimeout :=  1800 ; time in seconds. 30 minutes of timeout. 
WaitForImage(&Px, &Py, image, timeout := DefaultTimeout) {
	
	Loop {
		Sleep(1000)
		; MsgBox "Looking for " image
		if (A_Index > timeout) {
			MsgBox "Failed to find " image " in time. Aborting."
			exit
		}
		if ImageSearch(&Px, &Py, 0, 0, 2000, 2000, image) {
			break
		}
	}
}

WaitForNotImage(image, timeout := DefaultTimeout) {
	
	Loop {
		Sleep(1000)
		; MsgBox "Looking for " image
		if (A_Index > timeout) {
			MsgBox "Failed to find " image " in time. Aborting."
			exit
		}
		if !(ImageSearch(&Px, &Py, 0, 0, 2000, 2000, image)) {
			break
		}
	}
}


^j::
{
	Loop read "tables.txt" {
		Send "^a" A_LoopReadLine
		Send "{Enter}"
		WaitForImage(&Px, &Py, "data_browser_selection.png")
		Send "{Up}^a2147483646{Up}^a9999{F8}"
		WaitForImage(&Px, &Py, "se16_result.png")
		Send "+{F8}"
		WaitForImage(&Px1, &Py1, "filetype_selection_dialogue.png")
		Send "{Down}{Enter}"
		WaitForImage(&Px, &Py, "save_file_options.png")
		Send A_LoopReadLine ".tsv{Enter}"
		WaitForNotImage("save_file_options.png")
		Send "{F3}"
		WaitForImage(&Px, &Py, "data_browser_selection.png")
		Send "{F3}"
		WaitForImage(&Px, &Py, "table_name.png")
	}
}