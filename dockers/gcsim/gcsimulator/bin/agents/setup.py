#
# Copyright (c) 2019-2020 by University of Campania "Luigi Vanvitelli".
# Developers and maintainers: Salvatore Venticinque, Dario Branco.
# This file is part of GreenCharge
# (see https://www.greencharge2020.eu/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Setup
=======================================
This agent deals with the creation of the message queue.
"""

###########################****************** IMPORT LIBRARIES SECTION ************************#########################
import spade
import os
from spade.behaviour import *
import xml.etree.ElementTree as ET
import queue
import glob
from shutil import copy2
import csv
import shutil
from utils.config import Configuration
import logging
from os import listdir
import copy

LOGFILE = '/home/gc/simulator/gcdaemon.log'

# logging.basicConfig(filename=LOGFILE, filemode= 'w', level=print)


# dir1 = os.path.dirname(os.path.realpath(__file__))
###########################****************** END IMPORT LIBRARIES SECTION ************************####################


###########################****************** DEFINE CLASS SECTION ************************###########################
# ANY DEVICE IS DEFINED BY A A COMPLEX OBJECT

class AbstractDevice:
    """This class defines an abstract device, will be implemented by other classes."""
    def __init__(self, id='0', house='0', type='0', name='0'):
        """
        Args:
            id: The device's id.
            house: The house where the device is located.
            type: The device's type .
            name: The device's name.
        """
        self.type = type
        self.id = id
        self.house = house
        self.name = name


class BackGroundLoad(AbstractDevice):
    """This class defines an background load."""
    def __init__(self, id='0', house='0', name='0'):
        """
        Args:
            id: The device's id.
            house: The house where the device is located.
            name: The device's name.
        """
        super(BackGroundLoad, self).__init__(id, house, "backgroundload", name)


class HeaterCooler(AbstractDevice):
    """This class defines an heater/cooler device."""
    def __init__(self, id='0', house='0', name='0'):
        """
        Args:
            id: The device's id.
            house: The house where the device is located.
            name: The device's name.
        """
        super(HeaterCooler, self).__init__(id, house, "heaterCooler", name)


class EV(AbstractDevice):
    """This class defines an EV device."""
    def __init__(self, id=0, house=0, chargingPoint=0, name='0', capacity='0', max_ch_pow_ac='0', max_ch_pow_cc='0',
                 max_dis_pow_ac='0', max_dis_pow_cc='0', max_all_en='0', min_all_en='0', sb_ch='0', sb_dis='0',
                 ch_eff='0', dis_eff='0',lat=0.0,long=0.0):
        """
        Args:
            id: The device's id.
            house: The house where the device is located.
            chargingPoint: The chargingPoint where the device is located.
            name: The device's name.
            capacity:  It is the maximum amount of energy can be stored.
            max_ch_pow_ac: Max charging power when alternate current is used.
            max_ch_pow_cc: Max charging power when direct current is used.
            max_dis_pow_ac: Max discharging power in alternate current.
            max_dis_pow_cc: Max discharging power in direct current.
            max_all_en: Maximum allowed energy can be stored as a percentage of the capacity.
            min_all_en: Minimum allowed energy must be stored as a percentage of the capacity.
            sb_ch: Energy threshold above which the charging efficiency decrease.
            sb_dis: Energy threshold below the discharging efficiency decrease.
            ch_eff: This parameter must be multiplied to the nominal maximum charging power to obtain the actual maximum charging power above sb_ch.
            dis_eff: This parameter must be multiplied to the nominal maximum discharging power to obtain the actual maximum discharging power below sb_dis.
        """
        super(EV,self).__init__(id, house, "EV", name)
        self.cp = chargingPoint
        self.capacity = capacity
        self.max_ch_pow_ac = max_ch_pow_ac
        self.max_ch_pow_cc = max_ch_pow_cc
        self.max_dis_pow_cc = max_dis_pow_cc
        self.max_dis_pow_ac = max_dis_pow_ac
        self.max_all_en = max_all_en
        self.min_all_en = min_all_en
        self.sb_ch = sb_ch
        self.sb_dis = sb_dis
        self.ch_eff = ch_eff
        self.dis_eff = dis_eff
        self.found = 0
        self.lat=lat
        self.long=long

class Battery(AbstractDevice):
    """This class defines an Battery device."""

    def __init__(self, id=0, house=0, name='0', capacity='0', max_ch_pow_ac='0', max_ch_pow_cc='0',
                 max_dis_pow='0', max_all_en='0', min_all_en='0', sb_ch='0', sb_dis='0', ch_eff='0',
                 dis_eff='0'):
        """
        Args:
            id: The device's id.
            house: The house where the device is located.
            name: The device's name.
            capacity:  It is the maximum amount of energy can be stored.
            max_ch_pow_ac: Max charging power when alternate current is used.
            max_ch_pow_cc: Max charging power when direct current is used.
            max_dis_pow_ac: Max discharging power.
            max_all_en: Maximum allowed energy can be stored as a percentage of the capacity.
            min_all_en: Minimum allowed energy must be stored as a percentage of the capacity.
            sb_ch: Energy threshold above which the charging efficiency decrease.
            sb_dis: Energy threshold below the discharging efficiency decrease.
            ch_eff: This parameter must be multiplied to the nominal maximum charging power to obtain the actual maximum charging power above sb_ch.
            dis_eff: This parameter must be multiplied to the nominal maximum discharging power to obtain the actual maximum discharging power below sb_dis.
        """
        self.id = id
        self.house = house
        self.name = name
        self.type = "battery"
        self.capacity = capacity
        self.max_ch_pow_ac = max_ch_pow_ac
        self.max_ch_pow_cc = max_ch_pow_cc
        self.max_dis_pow = max_dis_pow
        self.max_all_en = max_all_en
        self.min_all_en = min_all_en
        self.sb_ch = sb_ch
        self.sb_dis = sb_dis
        self.ch_eff = ch_eff
        self.dis_eff = dis_eff


class Device(AbstractDevice):
    """This class defines a schedulable device or a producer device."""

    def __init__(self, id='0', type='0', name='0', house='0'):
        """
        Args:
            id: The device's id.
            type: The device's type .
            name: The device's name.
            house: The house where the device is located.
        """
        super().__init__(id, house, type, name)


class Abstract_event:
    """This class defines an abstract event."""
    def __init__(self, device='0', house='0', creation_time='0', type2=0):
        """
        Args:
            device: The device to which the event refers
            house: The house where the device is located.
            creation_time: The time in which the event has to be triggered
            type2: Type of the event
        """
        self.device = device
        self.type = type2
        self.creation_time = creation_time
        self.house = house


class EventGeneral(Abstract_event):
    """This class defines a schedulable event."""
    def __init__(self, device='0', house='0', est='0', lst='0', creation_time='0', profile='0', type2=0):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            est: The earliest start time.
            lst: The latest start time.
            creation_time: The time in which the event has to be triggered.
            profile: The consumption profile the device has to perform.
            type2: The event type.
        """
        super(EventGeneral, self).__init__(device, house, creation_time, type2)
        self.est = est
        self.lst = lst
        self.profile = profile


class EventDelete(Abstract_event):
    """This class defines a delete event."""

    def __init__(self, device='0', house='0', creation_time='0', consumption=0):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            creation_time: The time in which the event has to be triggered.
            consumption: Total consumption energy value.
        """
        self.device = device
        self.type = "delete"
        self.creation_time = creation_time
        self.house = house
        self.consumption = consumption


class EventEcar(Abstract_event):
    """This class defines an EV event."""

    def __init__(self, device='0', house='0', Soc_at_arrival='0', booking_time='0', planned_arrival_time='0'
                 , planned_departure_time='0', actual_arrival_time='0', actual_departure_time='0',
                 target_soc='0', v2g='0', priority='0', v2gminsoc='0',lat=00.00,long=00.00):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            Soc_at_arrival: The status of charge at plug-in time.
            booking_time: The booking time of charging session.
            planned_arrival_time: The planned arrival time to the charging point.
            planned_departure_time: The planned departure time from the charging point.
            actual_arrival_time: The actual arrival time to the charging point.
            actual_departure_time: The actual departure time from the charging point.
            target_soc: The desidered status of charge at plug-out time.
            v2g: Flag to set in order to use vehicle to grid.
            priority: Set the priority charging for the charging session.
        """
        self.device = device
        self.type = "EV"
        self.creation_time = booking_time
        self.house = house
        self.Soc_at_arrival = Soc_at_arrival
        self.planned_arrival_time = planned_arrival_time
        self.planned_departure_time = planned_departure_time
        self.actual_arrival_time = actual_arrival_time
        self.actual_departure_time = actual_departure_time
        self.v2g = v2g
        self.target_soc = target_soc
        self.priority = priority
        self.v2gminsoc = v2gminsoc
        self.lat=lat
        self.long=long


class EventBattery(Abstract_event):
    """This class defines a battery event."""
    def __init__(self, device='0', house='0', Soc_at_arrival='0', booking_time='0', start_time='0', end_time='0',
                 target_soc='0'):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            Soc_at_arrival: The status of charge at start time.
            booking_time: The time in which the battery entered into the system.
            start_time: The time in which the battery starts to work.
            end_time: The time in which the battery stops to work.
            target_soc: The desidered status of charge at the end time.
        """
        self.device = device
        self.type = "BATTERY"
        self.creation_time = booking_time
        self.house = house
        self.Soc_at_arrival = Soc_at_arrival
        self.start_time = start_time
        self.end_time = end_time
        self.target_soc = target_soc


class EventProducer(Abstract_event):
    """This class defines a producer event."""
    def __init__(self, device='0', house='0', est='0', lst='0', creation_time='0', profile='0', type2=0,
                 energycost='0'):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            creation_time: The time in which the producer entered into the system.
            profile: The production profile.
            type2: The event type.
            energycost: The energy cost.
        """
        self.device = device
        self.type = "load"
        self.creation_time = creation_time
        self.profile = profile
        self.house = house
        self.count = 0
        self.energycost = energycost
        self.est = est
        self.lst = lst


class EventBackground(Abstract_event):
    """This class defines a background load event."""

    def __init__(self, device='0', house='0', creation_time='0', profile='0'):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            creation_time: The time in which the background load entered into the system.
            profile: The consumption profile.
        """
        self.device = device
        self.creation_time = creation_time
        self.profile = profile
        self.house = house
        self.type = "backgroundload"


class EventHeaterCooler(Abstract_event):
    """This class defines a heater/cooler load event."""
    def __init__(self, device='0', house='0', creation_time='0', profile='0'):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            creation_time: The time in which the heater/cooler load entered into the system.
            profile: The consumption profile.
        """
        self.device = device
        self.creation_time = creation_time
        self.profile = profile
        self.house = house
        self.type = "heatercooler"


class Energy_Cost():
    """This class defines an energy cost  event."""
    def __init__(self, type='0', profile='0'):
        """
        Args:
            type: Type of event.
            profile: The energy cost profile.
        """
        self.type = "energy_cost"
        self.profile = profile


class Energy_Mix():
    """This class defines an energy mix event."""
    def __init__(self, type='0', profile='0'):
        """
        Args:
            type: Type of event.
            profile: The energy cost profile.
        """
        self.type = "energy_mix"
        self.profile = profile


class Neighborhood():
    """This class defines a neighborhood."""
    def __init__(self, type='0', peakload='0'):
        """
        Args:
            type: Type of energy Hub.
            peakload: The power peak.
        """
        self.type = "neighborhood"
        self.peakload = peakload


class House():
    """This class defines an house."""
    def __init__(self, type='0', id='0', peakload='0', numcp=0):
        """
        Args:
            type: Type of energy Hub.
            id: The id of energy hub.
            peakload: The power peak.
            numcp: The number of charging point the house has.
        """
        self.type = "house"
        self.id = id
        self.peakload = peakload
        self.numcp = numcp


class ChargingStation():
    """This class defines a charging Station."""
    def __init__(self, type='0', id='0', peakload='0', numcp=0,lat=0.0,long=0.0):
        """
        Args:
            type: Type of energy Hub.
            id: The id of energy hub.
            peakload: The power peak.
            numcp: The number of charging point the house has.
            lat: The latitude of the CS.
            long: The longitude of the CS.
        """
        self.type = "chargingStation"
        self.id = id
        self.peakload = peakload
        self.numcp = numcp
        self.lat=lat
        self.long=long

class ChargingPoint():
    """This class defines a charging Point."""

    def __init__(self, type='0', id='0', houseid='0', conntype='0', peakload='0'):
        """
        Args:
            type: Type of energy Hub.
            id: The id of energy hub.
            houseid: The id of energy hub parent.
            conntype: Type of connectors the charging point has (AC/DC)
            peakload: The power peak.
        """
        self.type = "chargingPoint"
        self.houseid = houseid
        self.id = id
        self.peakload = peakload
        self.connection_type = conntype


###########################****************** END DEFINE CLASS SECTION ************************###################################################


###########################****************** UTIL VARIABLES SECTION ************************###################################################
from dataclasses import dataclass


##########################################################
# Override the comparison methods for the shared queue   #
##########################################################
@dataclass(order=False)
class EnqueuedEvent:
    """This class overrides the comparison methods for the shared queue."""

    unique_id = 0

    def __init__(self, timestamp, event, unique_id=None):
        """
        Args:
            timestamp: Event time.
            event: The event.
            unique_id: An unique id in case of same timestamp for two events.
        """
        self.timestamp = timestamp
        self.event = event
        if unique_id is None:
            EnqueuedEvent.unique_id +=1
            self.unique_id = EnqueuedEvent.unique_id
        else:
            self.unique_id = unique_id

    def __lt__(self, other):
        if self.timestamp == other.timestamp:
            return self.unique_id < other.unique_id
        else:
            return self.timestamp < other.timestamp

    def __gt__(self, other):
        if self.timestamp == other.timestamp:
            return self.unique_id > other.unique_id
        return self.timestamp > other.timestamp

    def __eq__(self, other):
        return self.timestamp == other.timestamp and self.unique_id == other.id

    def __ne__(self, other):
        return not  self.timestamp == other.timestamp and self.unique_id == other.id


####################################################################
# Class entities, used to enqueue/get an object in/from the queue  #
####################################################################
class Entities:
    """This class is used to enqueue/get an object in/from the queue."""

    listDevice = []  # IN THIS LIST WILL BE STORED ALL THE LOADS
    listPanels = []  # IN THIS LIST WILL BE STORED ALL THE PRODUCERS
    listEvent = []
    sharedQueue = queue.PriorityQueue()

    @classmethod
    def enqueue_event(cls, timestamp, event, unique_id=None):
        """
        This method is used to enqueue an event in the event queue.
        Args:
            timestamp: Event time.
            event: The event.
            unique_id: An unique id in case of same timestamp for two events.
        """
        cls.sharedQueue.put(EnqueuedEvent(timestamp, event, unique_id))

    @classmethod
    def next_event(cls):
        """
        This method is used to dequeue an event from the event queue.
        """
        item = cls.sharedQueue.get()
        return   (item.timestamp, item.event, item.unique_id)

###########################****************** END UTIL VARIABLES SECTION ************************###################################################


###########################********************** METHODS SECTION ***************************###################################################
###########################*************** ANY ACTION IS DEFINED BY A METHOD ****************###################################################



#
#############################################################################################################
# createDevicesList() READS FROM A FILE ALL THE DEVICES, SORTS THEM BY TYPE AND APPEND THEM TO DEVICE LIST  #
#############################################################################################################
def createDevicesList():
    """ This method read from neighborhood.xml all the devices, sort them by type and append them to device list."""
    workingdir = Configuration.parameters['runtime_dir']
    date = Configuration.parameters['date'] + " 00:00:00"
    datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
    timestamp = datetime.timestamp(datetime_object) + 7200


    print("runtime folder: " + workingdir)
    f = open(workingdir + "/xml/neighborhood.xml", "r")
    fileIntero = f.read()
    root = ET.fromstring(fileIntero)
    neigh = Neighborhood('neighborhood', root.get('peakLoad2'))
    Entities.enqueue_event(timestamp, neigh)
    for energycost in root.findall('energyCost'):
        energycost = Energy_Cost('energyCost', energycost.find('profile').text)
        Entities.enqueue_event(timestamp, energycost)
    for energyMix in root.findall('energyMix'):
        energyMix = Energy_Mix('energyMix', energyMix.find('profile').text)
        Entities.enqueue_event(timestamp, energyMix)

    # Inserisci qui il codice per la creazione del neighborhood
    for house in root.findall('house'):  # READ XML FILE
        # inserisci qui il codice per la creazione di una house
        houseId = house.get('id')
        housedev = House('house', houseId, house.get('peakLoad'), 0)

        for user in house.findall('user'):
            for deviceElement in user.findall('device'):
                deviceId = deviceElement.find('id').text
                type = deviceElement.find('type').text
                name = deviceElement.find('name').text
                c = Device(deviceId, type, name, houseId)
                Entities.listDevice.append(c)
            for OtherElement in user.findall('heatercooler'):
                print("new heatercooler")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                c = HeaterCooler(deviceId, houseId, name)
                Entities.listDevice.append(c)

            for OtherElement in user.findall('backgroundload'):
                print("new bg")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                c = BackGroundLoad(deviceId, houseId, name)
                Entities.listDevice.append(c)
            for OtherElement in user.findall('battery'):
                print("new battery")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                capacity = OtherElement.find('capacity').text
                maxchpowac = OtherElement.find('maxchpowac').text
                maxchpowcc = OtherElement.find('maxchpowcc').text
                maxdispow = OtherElement.find('maxdispow').text
                maxallen = OtherElement.find('maxallen').text
                minallen = OtherElement.find('minallen').text
                sbch = OtherElement.find('sbch').text
                sbdis = OtherElement.find('sbdis').text
                cheff = OtherElement.find('cheff').text
                dis_eff = OtherElement.find('dis_eff').text
                c = Battery(deviceId, houseId, name, capacity, maxchpowac, maxchpowcc, maxdispow, maxallen, minallen,
                            sbch, sbdis, cheff, dis_eff)
                Entities.listDevice.append(c)

            for cp in user.findall('ChargingPoint'):
                cpId = cp.get('id')
                cpdev = ChargingPoint('house', houseId, cpId, cp.get('ConnectorsType'), cp.get('peakLoad'))
                # sharedQueue.put((0,int(count),cpdev))

                housedev.numcp += 1
                # inserisci qui il codice per la creazione del Cp
                for OtherElement in cp.findall('ecar'):
                    deviceId = OtherElement.find('id').text
                    name = OtherElement.find('name').text
                    capacity = OtherElement.find('capacity').text
                    maxchpowac = OtherElement.find('maxchpowac').text
                    maxchpowcc = OtherElement.find('maxchpowcc').text
                    maxdispowac = OtherElement.find('maxdispowac').text
                    maxdispowcc = OtherElement.find('maxdispowdc').text

                    maxallen = OtherElement.find('maxallen').text
                    minallen = OtherElement.find('minallen').text
                    sbch = OtherElement.find('sbch').text
                    sbdis = OtherElement.find('sbdis').text
                    cheff = OtherElement.find('cheff').text
                    dis_eff = OtherElement.find('dis_eff').text
                    c = EV(deviceId, houseId, cpId, name, capacity, maxchpowac, maxchpowcc, maxdispowac, maxdispowcc
                           , maxallen, minallen, sbch, sbdis, cheff, dis_eff)
                    Entities.listDevice.append(c)
        Entities.enqueue_event(timestamp, housedev)
    for house in root.findall('chargingStation'):  # READ XML FILE
        # inserisci qui il codice per la creazione di una cs
        houseId = house.get('id')
        CSlat=house.find('lat').text
        CSlong=house.find('long').text
        housedev = ChargingStation('house', houseId, house.get('peakLoad'), house.get('CPinfo'),CSlat,CSlong)

        for user in house.findall('user'):
            userId = user.get('id')
            for deviceElement in user.findall('device'):
                deviceId = deviceElement.find('id').text
                type = deviceElement.find('type').text
                name = deviceElement.find('name').text
                c = Device(deviceId, type, name, houseId)
                Entities.listDevice.append(c)
            for OtherElement in user.findall('heatercooler'):
                print("new heatercooler")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                c = HeaterCooler(deviceId, houseId, name)
                Entities.listDevice.append(c)

            for OtherElement in user.findall('backgroundload'):
                print("new bg")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                c = BackGroundLoad(deviceId, houseId, name)
                Entities.listDevice.append(c)
            for OtherElement in user.findall('battery'):
                print("new buttery")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                capacity = OtherElement.find('capacity').text
                maxchpowac = OtherElement.find('maxchpowac').text
                maxchpowcc = OtherElement.find('maxchpowcc').text
                maxdispow = OtherElement.find('maxdispowac').text
                maxallen = OtherElement.find('maxallen').text
                minallen = OtherElement.find('minallen').text
                sbch = OtherElement.find('sbch').text
                sbdis = OtherElement.find('sbdis').text
                cheff = OtherElement.find('cheff').text
                dis_eff = OtherElement.find('dis_eff').text
                c = Battery(deviceId, houseId, name, capacity, maxchpowac, maxchpowcc, maxdispow, maxallen, minallen,
                            sbch, sbdis, cheff, dis_eff)
                Entities.listDevice.append(c)
            for cp in user.findall('ChargingPoint'):
                housedev.numcp += 1
                cpId = cp.get('id')
                # cpdev = ChargingPoint('house',houseId,cpId, cp.get('ConnectorsType'), cp.get('peakLoad'))
                # sharedQueue.put((0,int(count),cpdev))

                # inserisci qui il codice per la creazione del Cp
                for OtherElement in cp.findall('ecar'):
                    deviceId = OtherElement.find('id').text
                    name = OtherElement.find('name').text
                    capacity = OtherElement.find('capacity').text
                    maxchpowac = OtherElement.find('maxchpowac').text
                    maxchpowcc = OtherElement.find('maxchpowcc').text
                    maxdispowac = OtherElement.find('maxdispowac').text
                    maxdispowcc = OtherElement.find('maxdispowdc').text

                    maxallen = OtherElement.find('maxallen').text
                    minallen = OtherElement.find('minallen').text
                    sbch = OtherElement.find('sbch').text
                    sbdis = OtherElement.find('sbdis').text
                    cheff = OtherElement.find('cheff').text
                    dis_eff = OtherElement.find('dis_eff').text
                    c = EV(deviceId, houseId, cpId, name, capacity, maxchpowac, maxchpowcc, maxdispowac, maxdispowcc
                           , maxallen, minallen, sbch, sbdis, cheff, dis_eff)
                    Entities.listDevice.append(c)
        Entities.enqueue_event(timestamp,  housedev)

    for fleet in root.findall('fleet'):
        for OtherElement in fleet.findall('ecar'):
            deviceId = OtherElement.find('id').text
            name = OtherElement.find('name').text
            capacity = OtherElement.find('capacity').text
            maxchpowac = OtherElement.find('maxchpowac').text
            maxchpowcc = OtherElement.find('maxchpowcc').text
            maxdispowac = OtherElement.find('maxdispowac').text
            try:
                maxdispowcc = OtherElement.find('maxdispowdc').text
            except:
                maxdispowcc = OtherElement.find('maxdispowac').text
            maxallen = OtherElement.find('maxallen').text
            minallen = OtherElement.find('minallen').text
            sbch = OtherElement.find('sbch').text
            sbdis = OtherElement.find('sbdis').text
            cheff = OtherElement.find('cheff').text
            dis_eff = OtherElement.find('dis_eff').text
            c = EV(deviceId, -1, -1, name, capacity, maxchpowac, maxchpowcc, maxdispowac, maxdispowcc, maxallen
                   , minallen, sbch, sbdis, cheff, dis_eff)
            Entities.listDevice.append(c)





##############################################################################################
#  createEventList() READS FROM A FILE THE EVENTS INFORMATIONS AND APPEND THEM TO LOADSLIST  #
##############################################################################################
def createEventList():
    """ This method read from loads.xml the events info and append them to loadslist."""
    codeID = {}
    workingdir = Configuration.parameters['runtime_dir']
    path = Configuration.parameters['current_sim_dir']
    f = open(workingdir + "/xml/loads.xml", "r")
    fileIntero = f.read();
    root = ET.fromstring(fileIntero)
    for house in root:
        if house.tag != 'fleet':
            houseId = house.get('id')
            print(house.get('code'))
            codeID[house.get('code')] = houseId
            # print 'house id ' + houseId
            for user in house.findall('user'):
                userId = user.get('id')
                for device in user.findall('device'):
                    deviceId = device.find('id').text
                    est = device.find('est').text
                    lst = device.find('lst').text
                    creation_time = device.find('creation_time').text
                    type2 = device.find("type").text
                    if device.find('profile').text.endswith(' '):
                        profile = device.find('profile').text[:-1]
                        #copy2(path + "/Inputs/" + profile, workingdir + "/inputs")
                    else:
                        profile = device.find('profile').text
                        #copy2(path + "/Inputs/" + profile, workingdir + "/inputs")

                    for c in Entities.listDevice:
                        if deviceId == c.id and houseId == c.house:
                            if c.type == "Consumer":
                                e = EventGeneral(c, houseId, est, lst, creation_time, profile, "load")
                                Entities.listEvent.append(e)
                                #copy2(workingdir + "/Inputs/" + profile, workingdir + "/inputs")
                                copy2(workingdir + "/inputs/" + profile, workingdir + "/output/SH")
                            elif c.type == "Producer":
                                energycost = device.find('energy_cost').text
                                #copy2(workingdir + "/Inputs/" + profile, workingdir + "/inputs")
                                copy2(workingdir + "/inputs/" + profile, workingdir + "/output/PV")

                                e = EventProducer(c, houseId, est, lst, creation_time, profile, "load", energycost)

                                Entities.listEvent.append(e)
                                # CODICE PROVVISORIO
                                # H = int(creation_time) + 21600
                                # print(H)
                                # print(int(creation_time))
                                # e1= eventGeneral(c,houseId,est,lst,H,profile, "LoadUpdate")
                                # H1 = int(creation_time) + 2*21600
                            # print(H1)
                            # e2= eventGeneral(c,houseId,est,lst,H1,profile, "LoadUpdate")
                            # H2 = int(creation_time) + 3*21600
                        # print(H2)
                        # e3= eventGeneral(c,houseId,est,lst,H2,profile, "LoadUpdate")
                        # Entities.listEvent.append(e1)
                        # Entities.listEvent.append(e2)
                        # Entities.listEvent.append(e3)
                        # #FineCodiceProvvisorio
                for device in user.findall('backgroundload'):
                    deviceId = device.find('id').text
                    mydir = Configuration.mydir
                    if device.find('profile').text.endswith(' '):
                        profile = device.find('profile').text[:-1]
                        #copy2(path + "/Inputs/" + profile, workingdir + "/inputs")
                        copy2(workingdir + "/inputs/" + profile, path + "/Results/" + Configuration.parameters['user_dir'] + "/output/BG/")
                    else:
                        profile = device.find('profile').text
                        #copy2(path + "/Inputs/" + profile, workingdir + "/inputs")
                        copy2(workingdir + "/inputs/" + profile, path + "/Results/" + Configuration.parameters['user_dir'] + "/output/BG/")
                    for c in Entities.listDevice:
                        if deviceId == c.id and houseId == c.house:
                            if c.type == "backgroundload":
                                e = EventBackground(c, houseId, 0, profile)
                                Entities.listEvent.append(e)
                for device in user.findall('heatercooler'):
                    deviceId = device.find('id').text
                    if device.find('profile').text.endswith(' '):
                        profile = device.find('profile').text[:-1]
                        copy2(path + "/Inputs/" + profile, workingdir + "/inputs")
                    else:
                        profile = device.find('profile').text
                        copy2(path + "/Inputs/" + profile, workingdir + "/inputs")
                    for c in Entities.listDevice:
                        if deviceId == c.id and houseId == c.house:
                            if c.type == "heaterCooler":
                                e = EventHeaterCooler(c, houseId, 0, profile)
                                Entities.listEvent.append(e)
                for device in user.findall('battery'):
                    deviceId = device.find('id').text
                    for c in Entities.listDevice:
                        if deviceId == c.id and houseId == c.house:
                            if c.type == "battery":
                                aat = device.find('startTime').text
                                adt = device.find('endTime').text
                                creation_time = device.find('creation_time').text
                                soc = device.find('soc').text
                                targetSoc = device.find('targetSoc').text
                                e = EventBattery(c, houseId, soc, creation_time, aat, adt, targetSoc)
                                Entities.listEvent.append(e)
                for cp in user.findall('ChargingPoint'):
                    for device in cp.findall('ecar'):
                        deviceId = device.find('id').text
                        for c in Entities.listDevice:
                            if deviceId == c.id and houseId == c.house:
                                if c.type == "EV":
                                    pat = device.find('pat').text
                                    pdt = device.find('pdt').text
                                    aat = device.find('aat').text
                                    adt = device.find('adt').text
                                    creation_time = device.find('creation_time').text
                                    soc = device.find('soc').text
                                    targetSoc = device.find('targetSoc').text
                                    V2G = device.find('V2G').text
                                    priority = device.find('priority').text
                                    v2gminsoc = device.find('v2gminsoc').text
                                    EVlat=device.find('lat').text
                                    EVlong=device.find('long').text
                                    e = EventEcar(c, houseId, soc, creation_time, pat, pdt, aat, adt, targetSoc, V2G,
                                                  priority, v2gminsoc,EVlat,EVlong)
                                    Entities.listEvent.append(e)
    for house in root:
        if(house.tag == 'fleet'):
            for device in house.findall('ecar'):
                deviceId = device.find('id').text
                for c in Entities.listDevice:
                    if deviceId == c.id:
                        if c.type == "EV":
                            pat = device.find('pat').text
                            pdt = device.find('pdt').text
                            aat = device.find('aat').text
                            adt = device.find('adt').text
                            creation_time = device.find('creation_time').text
                            soc = device.find('soc').text
                            targetSoc = device.find('targetSoc').text
                            V2G = device.find('V2G').text
                            priority = device.find('priority').text
                            EVlat=device.find('lat').text
                            EVlong=device.find('long').text
                            try:
                                v2gminsoc = device.find('v2gminSoc').text
                            except:
                                v2gminsoc = '20'
                            cp = codeID[device.find('LOC').text]
                            if(c.found == 0):
                                c.found = 1
                                e = EventEcar(c, cp, soc, creation_time, pat, pdt, aat, adt, targetSoc, V2G, priority, v2gminsoc,EVlat,EVlong)
                            else:
                                c2= copy.deepcopy(c)
                                e = EventEcar(c2, cp, soc, creation_time, pat, pdt, aat, adt, targetSoc, V2G, priority, v2gminsoc,EVlat,EVlong)
                            print(e.device.id)
                            Entities.listEvent.append(e)

####################################################################################
#  Convert Timestamps of a timeseries of an X day in timestamps of simulation day  #
####################################################################################
def switchInTime():
    """ This method Convert Timestamps of a timeseries of an X day in timestamps of simulation day."""

    workingdir = Configuration.parameters['runtime_dir']
    date = Configuration.parameters['date'] + " 00:00:00"
    datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
    timestamp = datetime.timestamp(datetime_object)
    entry = []
    allFilenames = listdir(workingdir+'/inputs')
    csvFilenames = [ filename for filename in allFilenames if filename.endswith( ".csv" ) ]
    for file in csvFilenames:
            with open(workingdir + "/inputs/" + file, "r") as f:
                with open(workingdir + "/inputs/temp" + file, "w") as f2:
                    reader = csv.reader(f)
                    writer = csv.writer(f2, delimiter=' ')
                    first = 0
                    for data in reader:
                        entry = []
                        oldtimestamp = datetime.fromtimestamp(int(data[0].split(" ")[0]))
                        if(first==0):
                            oldDay = oldtimestamp.day
                            first =1
                        datetime_new = datetime(year=datetime_object.year, month=datetime_object.month,
                                                day=datetime_object.day, hour=oldtimestamp.hour,
                                                minute=oldtimestamp.minute, second=oldtimestamp.second)
                        seconds = datetime.timestamp(datetime_new)
                        newDay = oldtimestamp.day
                        if(oldDay != newDay):
                            seconds += 86400
                        entry.append(str(int(seconds)))
                        entry.append(data[0].split(",")[1])
                        writer.writerow(entry)
            os.remove(workingdir + "/inputs/" + file)
            os.rename(workingdir + "/inputs/temp" + file, workingdir + "/inputs/" + file)



################################################################
#  UPLOADINPUTREPOSITORY() enqueue objects in the shared queue #
################################################################
def uploadInInputRepository():
    """ This method enqueue objects in the shared queue."""
    print('i am here')
    date = Configuration.parameters['date'] + " 00:00:00"
    datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')

    timestamp = datetime.timestamp(datetime_object) +7200
    
    for c in Entities.listEvent:
        if c.device.type == "Consumer" or c.device.type == "Producer":
            est_data = datetime.fromtimestamp(int(c.est))
            lst_data = datetime.fromtimestamp(int(c.lst))
            ct_data = datetime.fromtimestamp(int(c.creation_time))
            midsecondsEST = (est_data.hour * 60 * 60) + (est_data.minute * 60) + est_data.second
            midsecondsLST = (lst_data.hour * 60 * 60) + (lst_data.minute * 60) + lst_data.second
            midsecondsCT = (ct_data.hour * 60 * 60) + (ct_data.minute * 60) + ct_data.second
            c.lst = str(int(timestamp + midsecondsLST))
            c.creation_time = str(int(timestamp + midsecondsCT))
            if c.creation_time != '0':
                c.creation_time = str(int(timestamp + midsecondsCT))
            else:
                c.creation_time = str(int(timestamp))
            if c.est != '0':
                c.est = str(int(timestamp))
            else:
                c.est = str(int(timestamp))
            if c.device.type == "Consumer":
                Entities.enqueue_event(int(c.creation_time) + 100 + 7200, c)
            if c.device.type == "Producer":
                Entities.enqueue_event(int(c.creation_time)+ 7200,  c)

        # print("inserito")
        elif c.device.type == "EV":
            print("new EV")
            print(c.device.id)
            book_time = datetime.fromtimestamp(int(c.creation_time))
            planned_arrival_time = datetime.fromtimestamp(int(c.planned_arrival_time))
            planned_departure_time = datetime.fromtimestamp(int(c.planned_departure_time))
            actual_arrival_time = datetime.fromtimestamp(int(c.actual_arrival_time))
            actual_departure_time = datetime.fromtimestamp(int(c.actual_departure_time))
            midseconds_book_time = (book_time.hour * 60 * 60) + (book_time.minute * 60) + book_time.second
            midseconds_planned_arrival_time = (planned_arrival_time.hour * 60 * 60) + \
                                              (planned_arrival_time.minute * 60) + (planned_arrival_time.second)
            midseconds_planned_departure_time = (planned_departure_time.hour * 60 * 60) + \
                                                (planned_departure_time.minute * 60) + planned_departure_time.second
            midseconds_actual_departure_time = (actual_departure_time.hour * 60 * 60) + \
                                               (actual_departure_time.minute * 60) + actual_departure_time.second
            midseconds_actual_arrival_time = (actual_arrival_time.hour * 60 * 60) + \
                                             (actual_arrival_time.minute * 60) + actual_arrival_time.second
            c.creation_time = str(int(timestamp + midseconds_book_time))
            c.planned_arrival_time = str(int(timestamp) + int(c.planned_arrival_time))
            c.planned_departure_time = str(int(timestamp) + int(c.planned_departure_time))
            c.actual_arrival_time = str(int(timestamp) + int(c.actual_arrival_time))
            c.actual_departure_time = str(int(timestamp) + int(c.actual_departure_time))
            c.device.type = "CREATE_EV"
            '''
            print(c.device.id)
            print("timestamp = " + str(timestamp))
            print("BookingTime  = " + str(c.creation_time))
            print("arrival_Time =  " + str(c.actual_arrival_time))
            print("departure_Time = " + str(c.actual_departure_time))
            '''
            Entities.enqueue_event(timestamp, c)

            Entities.enqueue_event(int(c.creation_time)+ 7200,  c)

            Entities.enqueue_event(int(c.actual_arrival_time)+ 7200,  c)

            Entities.enqueue_event(int(c.actual_departure_time)+ 7200,  c)

        elif c.device.type == "heaterCooler":
            c.creation_time = str(int(timestamp))
            Entities.enqueue_event(int(c.creation_time)+ 7200,  c)
        elif c.device.type == "backgroundload":
            c.creation_time = str(int(timestamp))
            Entities.enqueue_event(int(c.creation_time)+ 7200,  c)
        elif c.device.type == "battery":
            est_data = datetime.fromtimestamp(int(c.start_time))
            lst_data = datetime.fromtimestamp(int(c.end_time))
            ct_data = datetime.fromtimestamp(int(c.creation_time))
            midsecondsEST = ((est_data.hour) * 60 * 60) + ((est_data.minute) * 60) + (est_data.second)
            midsecondsLST = ((lst_data.hour) * 60 * 60) + ((lst_data.minute) * 60) + (lst_data.second)
            midsecondsCT = ((ct_data.hour) * 60 * 60) + ((ct_data.minute) * 60) + (ct_data.second)
            c.start_time = str(int(timestamp) + int(c.start_time))
            c.end_time = str(int(timestamp)+int(c.end_time))
            #c.end_time = str(int(timestamp))
            c.creation_time = str(int(timestamp)+ int(c.creation_time))
            #c.creation_time = str(int(timestamp))
            Entities.enqueue_event(int(c.creation_time)+ 7200,  c)


###################################################
#  This Method create all simulation directories  #
###################################################
def makeNewSimulation(pathneigh, pathload):
    """
    This Method create all simulation directories.
    Args:
        pathneigh: The neighborhood.xml path.
        pathload: The loads.xml path.
    """
    date = Configuration.parameters['date'] + " 00:00:00"
    datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
    date2 = date.split()
    dir1 = Configuration.parameters['current_sim_dir']


    newdir = date2[0].replace('/', '_')

    sim_temp = newdir.split("_")
    lock = False
    if len(sim_temp[0]) == 1:
        sim_temp[0] = " 0 " + sim_temp[0]
        lock = True
    if len(sim_temp[1]) == 1:
        sim_temp[1] = "0" + sim_temp[1]
        lock = True

    if lock:
        newdir = sim_temp[0] + "_" + sim_temp[1] + "_" + sim_temp[2]

    dirCount = 1
    while os.path.exists(dir1 + "/Results/" + newdir + "_" + str(dirCount)):
        dirCount += 1
    os.mkdir(dir1 + "/Results/" + newdir + "_" + str(dirCount), 0o777)
    os.chmod(dir1 + "/Results/" + newdir + "_" + str(dirCount), 0o777)

    workingdir = Configuration.parameters['runtime_dir']
    try:
        os.mkdir(dir1 + "/Results/" + newdir + "_" + str(dirCount) + '/inputs' , 0o666)
        os.chmod(dir1 + "/Results/" + newdir + "_" + str(dirCount) + '/inputs' , 0o777)
    except:
        None

    os.mkdir(workingdir + "/xml", 0o666)
    os.chmod(workingdir + "/xml", 0o777)

    os.mkdir(workingdir + "/output", 0o666)
    os.chmod(workingdir + "/output", 0o777)


    path = Configuration.parameters['current_sim_dir']
    try:
        os.mkdir(workingdir + "/inputs", 0o666)
        os.chmod(workingdir + "/inputs", 0o777)
    except:
        None
    
    os.mkdir(workingdir + "/output/HC/", 0o666)
    os.chmod(workingdir + "/output/HC/", 0o777)

    os.mkdir(workingdir + "/output/BG/", 0o666)
    os.chmod(workingdir + "/output/BG/", 0o777)

    os.mkdir(workingdir + "/output/EV/", 0o666)
    os.chmod(workingdir + "/output/EV/", 0o777)

    os.mkdir(workingdir + "/output/PV/", 0o666)
    os.chmod(workingdir + "/output/PV/", 0o777)

    os.mkdir(workingdir + "/output/SH/", 0o666)
    os.chmod(workingdir + "/output/SH/", 0o777)


    if os.path.exists(path + "/output/"):
        shutil.rmtree(path + "/output/")
        os.mkdir(path + "/output/", 0o666)
        os.chmod(path + "/output/", 0o777)

        os.mkdir(path + "/output/BG/", 0o666)
        os.chmod(path + "/output/BG/", 0o777)

        os.mkdir(path + "/output/HC/", 0o666)
        os.chmod(path + "/output/HC/", 0o777)

        os.mkdir(path + "/output/EV/", 0o666)
        os.chmod(path + "/output/EV/", 0o777)

        os.mkdir(path + "/output/SH/", 0o666)
        os.chmod(path + "/output/SH/", 0o777)

    else:
        os.mkdir(path + "/output/", 0o666)
        os.chmod(path + "/output/", 0o777)

        os.mkdir(path + "/output/BG/", 0o666)
        os.chmod(path + "/output/BG/", 0o777)

        os.mkdir(path + "/output/HC/", 0o666)
        os.chmod(path + "/output/HC/", 0o777)

        os.mkdir(path + "/output/EV/", 0o666)
        os.chmod(path + "/output/EV/", 0o777)

        os.mkdir(path + "/output/SH/", 0o666)
        os.chmod(path + "/output/SH/", 0o777)



    copy2(pathneigh, workingdir + "/xml")

    os.rename(workingdir + "/xml/" + os.path.basename(pathneigh), workingdir + "/xml/neighborhood.xml")
    copy2(pathload, workingdir + "/xml")
    os.rename(workingdir + "/xml/" + os.path.basename(pathload), workingdir + "/xml/loads.xml")
    csvfiles = glob.glob(dir1 + "/Inputs/*.csv")

    for csvfile in csvfiles:
        print(csvfile)
        copy2(csvfile, workingdir + "/inputs")
    print("runtime folders created")

    """for filename in os.listdir(workingdir+"/inputs"):
        src = workingdir+"/inputs/"+filename
        dst= os.path.splitext(filename)
        newFirstText = dst[0][:-1] + str(dirCount)
        dst = workingdir+"/inputs/"+newFirstText+dst[1]
        os.rename(src, dst)"""





######################################################################################################
#  This method copy the scenario to the web directory to allow the scheduler to download the files.  #
######################################################################################################
def copyInscheduler():
    """ This method copy the scenario to the web directory to allow the scheduler to download the files. """
    workingdir = Configuration.parameters['runtime_dir']
    mydir = Configuration.parameters['user_dir']
    webdir = Configuration.parameters['webdir']
    src_files = os.listdir(workingdir + "/inputs/")
    # mydir = .split("/")[-1]
    # print ( myd i r)

    try:
        os.mkdir(webdir + "/" + mydir)
        os.mkdir(webdir + "/" + mydir + "/output")
    except:
        shutil.rmtree(webdir + "/" + mydir+"/")
        os.mkdir(webdir + "/" + mydir)
        os.mkdir(webdir + "/" + mydir + "/output")

    for file_name in src_files:
        full_file_name = os.path.join(workingdir + "/inputs/", file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(
                full_file_name, webdir + "/" +mydir)

####********************** END METHODS SECTION ***************************###################################################
###########################*************** ANY ACTION IS DEFINED BY A METHOD ****************###################################################


###########################********************** SPADE METHODS SECTION ***************************######################################### # #########
###########################*************** ANY ACTION IS DEFINED BY A METHOD *** * *** * ********################## # ### # ##### # ######################



class ExternalSourceAgent(spade.agent.Agent):
    """This Agent deals to the creation of simulation data from xml files."""
    def __init__(self, address, passw,
                 pathneigh, pathload):
        """
        Args:
            address: Agent Address.
            passw: Agent Password.
            pathneigh: The neighborhood.xml path.
            pathload: The loads.xml path.
        """
        super(ExternalSourceAgent, self).__init__(address, passw)
        self.pathneighbor = pathneigh
        self.pathload2 = pathload


    def simulation_setup(self):
        Entities.sharedQueue.queue.clear()
        Entities.listDevice = []  # IN THIS LIST WILL BE STORED ALL THE LOADS
        Entities.listPanels = []  # IN THIS LIST WILL BE STORED ALL THE PRODUCERS
        Entities.listEvent = []
        print('hello')
        makeNewSimulation(self.pathneighbor, self.pathload2)
        #switchInTime()

        createDevicesList()
        print("List Created.")

        createEventList()
        print("Information Added.")
        uploadInInputRepository()
        copyInscheduler()

        date = Configuration.parameters['date'] + " 00:00:00"
        datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
        print(datetime_object)
        print("Information Uploaded.")

###########################********************** END SPADE METHODS SECTION ***************************###################################################
###########################*************** ANY ACTION IS DEFINED BY A METHOD ****************###################################################
