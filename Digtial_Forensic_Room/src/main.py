"""
The main program entrance file.  The contents of this should be:
* Identification of the platform and version.
* imports of the project components
* Call to initialize the system
"""

# Python imports

# Extron Library Imports
from extronlib import Platform, Version, event
from extronlib.device import ProcessorDevice, UIDevice
from extronlib.ui import *
import modules.device.extr_matrix_DTP_CrossPoint_82_84_4kSeriesv1872 as SwitcherModule
import modules.device.lg_display_xxUR640S9UD_Series_v1_0_0_0 as LGDisplayModule
from modules.helper.ConnectionHandler import GetConnectionHandler 
print('ControlScript', Platform(), Version())

processor = ProcessorDevice('MainProcessor')
panel = UIDevice('PrimaryTouchpanel')


switcher01 = SwitcherModule.SSHClass('192.168.1.12', 22023, Credentials=('admin', '8012662428'), Model='DTP CrossPoint 84 4K IPCP SA')
switcher01_ch = GetConnectionHandler(switcher01, keepAliveQuery='Input', DisconnectLimit=15, pollFrequency=5)

display01 = LGDisplayModule.SerialOverEthernetClass('192.168.1.12',2003, 'TCP', Model='86UR640S9UD')
display02 = LGDisplayModule.SerialOverEthernetClass('192.168.1.12', 2004, 'TCP', Model='86UR640S9UD')
display01_ch = GetConnectionHandler(display01, keepAliveQuery='Power', DisconnectLimit=15, pollFrequency=5)
display02_ch = GetConnectionHandler(display02, keepAliveQuery='Power', DisconnectLimit=15, pollFrequency=5)

def disp01PowerHandler(command, value, qualifier):
    print(command)
    print(value)
    print(qualifier)
    
    

display01_ch.SubscribeStatus('Power', None, disp01PowerHandler)
# Project imports
import variables as v
import devices
import ui.tlp
import control.av
import system




startBtn = Button(panel, v.StartID)
shutdownBtn = Button(panel, v.ShutdownID)
shutdownConfirmBtn = Button(panel, v.ShutdownConfirmID)
shutdownCancelBtn = Button(panel, v.ShutdownCancelID)


def initialize():
    switcher01_ch.Connect()
    display01_ch.Connect()
    display02_ch.Connect()
    panel.ShowPage(v.PageStart)
    panel.HideAllPopups()

def startup():
    panel.ShowPopup(v.PopupStartingUp, v.WaitDuration)
    panel.HideAllPopups()
    panel.ShowPage(v.PageMain)
    panel.ShowPopup(v.PopupRouting)
    display01.Set('Power', 'On')
    display02.Set('Power', 'On')

def shutdown():
    panel.ShowPopup(v.PopupPoweringDown)
    panel.HideAllPopups()
    #Clear routes
    display01.Set('Power', 'Off')
    display02.Set('Power', 'Off')
    panel.ShowPage(v.PageStart)
    
@event(startBtn, 'Pressed')
def startBtnPressed(button, state):
    startup()

@event(shutdownBtn, 'Pressed')
def shutdownBtnPressed(button, state):
    if state == 'Pressed':
        panel.ShowPopup(v.PopupShutdown)
        button.SetState(1)
        
@event(shutdownConfirmBtn, 'Pressed')
def shutdownConfirmBtnPressed(button, state):
    if state == 'Pressed':
        shutdown()
        shutdownBtn.SetState(0)
    
@event(shutdownCancelBtn, 'Pressed')
def shutdownCancelBtnPressed(button, state):
    if state == 'Pressed':
        panel.HidePopup(v.PopupShutdown)
        panel.ShowPopup(v.PopupRouting)
        shutdownBtn.SetState(0)
    

initialize()
