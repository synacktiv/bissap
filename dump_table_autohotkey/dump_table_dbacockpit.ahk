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


^j::
{
	Loop read "tables.txt" {
		Send "^aSELECT * FROM " A_LoopReadLine
		Send "{F8}"
		WaitForImage(&Px, &Py, "save_to_file.PNG")
		Click Px + 2, Py + 2
		Sleep(100)
		Send "l"
		WaitForImage(&Px1, &Py1, "filetype_selection_dialogue.png")
		Send "{Down}{Enter}"
		WaitForImage(&Px, &Py, "save_file.bmp")
		Send A_LoopReadLine ".tsv{Enter}"
		WaitForImage(&Px, &Py, "input_query.png")
		Click Px + 10, Py + 5
		WaitForImage(&Px, &Py, "input_query_selected.png")
		Click 500, 500
		Sleep(500)
	}
}