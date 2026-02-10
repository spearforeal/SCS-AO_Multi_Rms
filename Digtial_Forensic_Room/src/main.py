"""
The main program entrance file.  The contents of this should be:
* Identification of the platform and version.
* imports of the project components
* Call to initialize the system
"""

# Python imports

# Extron Library Imports
from extronlib import Platform, Version, event
from extronlib.system import MESet
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


class Router:
    def __init__(self, switcher):
        self.switcher = switcher
        self.current_source = 0
        print('Router initialized')
    
    def set_source(self, src):
        self.current_source = src
        print('Source selected: {}'.format(src))

    def route_to(self, out_num, src=None, tie_type='Audio/Video', refresh=True):
        if src is not None:
            self.current_source = src
            print('Source overridden to {}'.format(src))
        print('Routing Input {} → Output {} ({})'.format(
            self.current_source, out_num, tie_type
        ))
        self.switcher.Set('MatrixTieCommand', None, {
            'Input': str(self.current_source),
            'Output': str(out_num),
            'Tie Type': tie_type
        })
        if refresh:
            print('Refreshing matrix')
            self.switcher.Set('RefreshMatrix', None)
        
    def clear_to(self, out_num, tie_type='Audio/Video', refresh=True):
        print('Clearing Output {}'.format(out_num))
        self.switcher.Set('MatrixTieCommand', None, {
            'Input': '0',
            'Output': str(out_num),
            'Tie Type': tie_type
        })
        if refresh:
            print('Refreshing matrix')
            self.switcher.Set('RefreshMatrix', None)
    

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
disp1PowerOnBtn = Button(panel, v.Disp1PowerOnID)
disp1PowerOffBtn = Button(panel, v.Disp1PowerOffID)
disp2PowerOnBtn = Button(panel, v.Disp2PowerOnID)
disp2PowerOffBtn = Button(panel, v.Disp2PowerOffID)
Src1Btn = Button(panel, v.Src1BtnID)
Src2Btn = Button(panel, v.Src2BtnID)
Src3Btn = Button(panel, v.Src3BtnID)
Src4Btn = Button(panel, v.Src4BtnID)
Src5Btn = Button(panel, v.Src5BtnID)
Src6Btn = Button(panel, v.Src6BtnID)
ClearBtn = Button(panel, v.ClearBtnID)
Dest1Btn = Button(panel, v.Dest1BtnID)
Dest2Btn = Button(panel, v.Dest2BtnID)
router = Router(switcher01)

src_btns_dict = {
    Src1Btn:1,
    Src2Btn:2, 
    Src3Btn:3,
    Src4Btn:4,
    Src5Btn:5,
    Src6Btn:6,
    ClearBtn:0 
}
dest_btns_dict = {
    Dest1Btn: 3,
    Dest2Btn: 4,
}
swSrcGroup = MESet(list(src_btns_dict.keys()))
swDestGroup = MESet(list(dest_btns_dict.keys()))


def disp01PowerHandler(command, value, qualifier):
    print('Display 1 power feedback: {}'.format(value))
    if value == 'On':
        disp1PowerOnBtn.SetState(1)
        disp1PowerOffBtn.SetState(0)
    else:
        disp1PowerOnBtn.SetState(0)
        disp1PowerOffBtn.SetState(1)

def disp02PowerHandler(command, value, qualifier):
    print('Display 2 power feedback: {}'.format(value))
    if value == 'On':
        disp2PowerOnBtn.SetState(1)
        disp2PowerOffBtn.SetState(0)
    else:
        disp2PowerOnBtn.SetState(0)
        disp2PowerOffBtn.SetState(1)

display01_ch.SubscribeStatus('Power', None, disp01PowerHandler)
display02_ch.SubscribeStatus('Power', None, disp02PowerHandler)
def initialize():
    switcher01_ch.Connect()
    display01_ch.Connect()
    display02_ch.Connect()
    display01.Update('Power')
    display02.Update('Power')
    panel.ShowPage(v.PageStart)
    panel.HideAllPopups()


def startup():
    print('Startup sequence start')
    panel.ShowPopup(v.PopupStartingUp, v.WaitDuration)
    panel.HideAllPopups()
    panel.ShowPage(v.PageMain)
    panel.ShowPopup(v.PopupRouting)
    print('Power displays On')
    display01.Set('Power', 'On')
    display02.Set('Power', 'On')
    display01.Update('Power')
    display02.Update('Power')
    print('Applying default routing')
    router.set_source(v.DefaultInput)
    router.route_to(3, refresh=False)
    router.route_to(4, refresh=True)
    print('Applying default routes')



def shutdown():
    print('Shutdown sequence begin')
    panel.ShowPopup(v.PopupPoweringDown)
    panel.HideAllPopups()
    print('Power displays off')
    display01.Set('Power', 'Off')
    display02.Set('Power', 'Off')
    display01.Update('Power')
    display02.Update('Power')
    panel.ShowPage(v.PageStart)
    print('Clearing matrix routes')
    router.clear_to(3, refresh=False) 
    router.clear_to(4, refresh=True) 
    print('Shutdown sequence complete')


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

@event(disp1PowerOnBtn, 'Pressed')
def disp1PowerOnBtnPressed(button, state):
    display01.Set('Power', 'On')
    display01.Update('Power')

@event(disp1PowerOffBtn, 'Pressed')
def disp1PowerOffBtnPressed(button, state):
    display01.Set('Power', 'Off')
    display01.Update('Power')
    
@event(disp2PowerOnBtn, 'Pressed')
def disp2PowerOnBtnPressed(button, state):
    display02.Set('Power', 'On')
    display02.Update('Power')

@event(disp2PowerOffBtn, 'Pressed')
def disp2PowerOffBtnPressed(button, state):
    display02.Set('Power', 'Off')
    display02.Update('Power')

@event(swSrcGroup.Objects, 'Pressed')
def onSrcPressed(button, state):
    src = src_btns_dict[button]
    print('Source button pressed → {}'.format(src))
    swSrcGroup.SetCurrent(button)
    router.set_source(src)



@event(swDestGroup.Objects, 'Pressed')
def onDestPressed(button, state):
    out_num = dest_btns_dict[button]
    print('Destination button pressed → Output {}'.format(out_num))
    swDestGroup.SetCurrent(button)
    router.route_to(out_num, refresh=True)
    


initialize()
