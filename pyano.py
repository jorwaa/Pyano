import time
import logging
import rtmidi as rtm
from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON

import os

try:
    input = raw_input
except NameError:
    # Python 3
    StandardError = Exception

NOTE = 60

apis = {
    rtm.API_WINDOWS_MM: "Windows MultiMedia",
}

available_apis = rtm.get_compiled_api()



def probe_ports():
    for api, api_name in apis.items():
        if api in available_apis:
            try:
                reply = input("Probe ports using the %s API? (Y/n) " % api_name)
                if reply.strip().lower() not in ['', 'y', 'yes']:
                    continue
            except (KeyboardInterrupt, EOFError):
                print('')
                break
    
    for name, class_ in (("input", rtm.MidiIn), ("output", rtm.MidiOut)):
        try:
            midi = class_(api)
            ports = midi.get_ports()
        except StandardError as exc:
            print("Could not probe MIDI %s ports: %s" % (name, exc))
            continue
    if not ports:
            print("No MIDI %s ports found." % name)
    else:
        print("Available MIDI %s ports:\n" % name)

        for port, name in enumerate(ports):
            print("[%i] %s" % (port, name))
        del midi
        port = input("Choose the port to use:")
        return int(port)

    print('')
    
def send_note(note, port):
    midiout = rtm.MidiOut()
    with (midiout.open_port(port) if midiout.get_ports() else
        midiout.open_virtual_port("Virtual Output yeah!")):
        note_on = [NOTE_ON, note, 112]
        note_off = [NOTE_OFF, note, 0]
        midiout.send_message(note_on)
        time.sleep(1)
        midiout.send_message(note_off)
        time.sleep(1)
    
    del midiout

def get_note(port_in, port_out):
    log = logging.getLogger('midiin_poll')
    logging.basicConfig(level='DEBUG')
    
    try:
        midiin, port_in_name = open_midiinput(port_in)
        #midiout = rtm.MidiOut
        midiout = (rtm.MidiOut()).open_port(port_out)
    except (EOFError, KeyboardInterrupt):
        return
    print("Listening...")
    print("To exit, press CTRL+C")

    try:
        timer = time.time()
        while True:
            msg = midiin.get_message()
            if msg:
                message, deltatime = msg
                #timer += deltatime
                #print("[%s] @%0.6f %r" % (port_in_name, timer, message))
                out_msg = [int(numeric_str) for numeric_str in message]
                #print("outmessage: %r" % out_msg)
                midiout.send_message(out_msg)
    except KeyboardInterrupt:
        print("Listening has stopped.")
    finally:
        print("Closing the port...")
        midiin.close_port()
        del midiin



def test():
    midiout = rtm.MidiOut()
    available_ports = midiout.get_ports()
    print(available_ports)

print("Starter probe_ports...")
port_in = probe_ports()
print("Chosen port: ", port_in)
print("Starting to listen...")
get_note(port_in, port_out = 0)