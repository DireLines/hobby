using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

public class Event{
	public int note;
	public int time;
	public string type;
	public int track;

	public Event (int a1, int a2, string a3, int a4){
		note = a1;
		time = a2;
		type = a3;
		track = a4;
	}
}

public class EventWithMicrosecondTime{
	public int note;
	public int time;
	public string type;
	public int track;
	public int timeMS;

	public EventWithMicrosecondTime (int a1, int a2, string a3, int a4, int a5){
		note = a1;
		time = a2;
		type = a3;
		track = a4;
		timeMS = a5;
	}
}
public class MidiParser : MonoBehaviour {
	//C# version of the MIDI parser for the game Music of the Spheres.
	//its job is to take in a MIDI file and some supplementary info
	//and produce a list of in game events with time stamps
	//to be referred to elsewhere in the code.

	//main function that will be called from elsewhere
	public List<Event> CreateGameEventList(string filename, List<int> tracknums, int startTime, int duration)
	{
		Debug.Log("Yo");
		List<Event> eventList = createEventList (filename, tracknums);
		eventList = adjustForTimeSignatureChanges (eventList);
		eventList = trimOverlappingEvents (eventList);
		eventList = timeSort (eventList);

		int numberOfSecondsToStretchTo = 65;
		eventList = stretchTime (eventList, numberOfSecondsToStretchTo);
//		printAllEvents (eventList);
		eventList = trimToInterval (eventList, startTime, duration);
		eventList = normalizeTimes (eventList);
		eventList = labelFirstAndLastEventsForEachNote (eventList, duration);
		eventList = timeSort (eventList);
		return eventList;
	}








	//shoves a file into a big list of byte objects
	private List<byte> getByteList(string filename)
	{
		byte[] bytesInArray = File.ReadAllBytes (filename);
		List<byte> bytesInList = new List<byte> ();
		foreach (byte b in bytesInArray) {
			bytesInList.Add (b);
		}
		return bytesInList;
	}

	private byte[] getByteArray(string filename)
	{
		byte[] bytes = File.ReadAllBytes (filename);
		return bytes;
	}

	//gets bits of a byte most significant first
	private string getBits(byte b)
	{
		string bitstring = "";
		for (int i = 7; i >= 0; i--) {
			bitstring += ((b >> i) & 1);
		}
		return bitstring;
	}

	//gets bits of a list of bytes most significant first
	private string getConcatBits(byte[] bytes){
		string bitstring = "";
		foreach (byte b in bytes) {
			bitstring += getBits (b);
		}
		return bitstring;
	}

	//byte --> decimal
	private int getIntValue(byte b)
	{
		return Convert.ToInt32 (getBits (b), 2);
	}

	private int getConcatIntValue(byte[] bytes)
	{
		return Convert.ToInt32 (getConcatBits (bytes), 2);
	}

	private T[] slice<T>(T[] arr, int begin, int end)
	{
		T[] result = new T[end - begin];
		for (int i = 0; i < end-begin; i++) {
			result [i] = arr [begin + i];
		}
		return result;
	}

	private List<T> sliceList<T>(List<T> list, int begin, int end)
	{
		List<T> result = new List<T> ();
		for (int i = begin; i < end; i++) {
			result.Add (list [i]);
		}
		return result;
	}
	//finds all indices of a sublist within a list. Returns a list of List<int> ordered pairs which are (beginning index of sublist, end index of sublist)
	private List<List<int>> findSubList<T>(List<T> sublist, List<T> list)
	{
		List<List<int>> results = new List<List<int>> ();
		List<int> indicesOfFirstThingInSublist = new List<int> ();
		for (int i = 0; i < list.Count; i++) {
			if (list [i].Equals (sublist [0])) {
				indicesOfFirstThingInSublist.Add (i);
			}
		}
		foreach (int ind in indicesOfFirstThingInSublist) {
			if (sliceList (list, ind, ind + sublist.Count).Equals (sublist)) {
				List<int> result = new List<int>(){ind,ind+sublist.Count-1};
				results.Add (result);
			}
		}
		return results;
	}

	private List<List<int>> findSubListFromArray<T>(T[] subarray, T[] arr)
	{
		List<List<int>> results = new List<List<int>> ();
		List<int> indicesOfFirstThingInSublist = new List<int> ();
		for (int i = 0; i < arr.Length; i++) {
			if (arr [i].Equals (subarray [0])) {
				indicesOfFirstThingInSublist.Add (i);
			}
		}
		foreach (int ind in indicesOfFirstThingInSublist) {
			if (slice (arr, ind, ind + subarray.Length).SequenceEqual (subarray)) {
				List<int> result = new List<int>(){ind,ind+subarray.Length-1};
				results.Add(result);
			}
		}
		return results;
	}

	//nice printing method which prints byte representation, decimal, hex, and binary
	private void printByteInfo(byte[] bytes)
	{
		for (int i = 0; i < bytes.Length; i++) {
			byte b = bytes [i];
			string bin = getBits (b);
			int dec = getIntValue(b);
			string hex = dec.ToString ("X");
			string str = System.Text.Encoding.ASCII.GetString(new byte[1]{b});
			Debug.Log (i + " : " + bin + "       " + dec + "        " + hex + "       " + str);
		}
	}

	//takes in a midi file and list of track numbers and creates a list of note on and off events
	//format of each event:
	//[note the event occurs in, absolute time of the event, 'on' or 'off', track of origin]
	//or, for time signature and tempo changes
	//[-1,absolute time, 'tempo change' or 'time signature change',(relevant info from MIDI message)]
	private List<Event> createEventList(string filename, List<int> tracknums){
		List<Event> result = new List<Event> ();
		byte[] bytes = getByteArray (filename);
		byte[] MThd = new byte[]{77,84,104,100};
		if (slice (bytes, 0, 4).SequenceEqual (MThd)) {
			//int sizeOfHeader = getConcatIntValue (slice (bytes, 4, 8));
			//int midiType = getConcatIntValue (slice (bytes, 8, 10));
			int numTracks = getConcatIntValue (slice (bytes, 10, 12));
			int numTicksPerQuarterNote = getConcatIntValue (slice (bytes, 12, 14));
			result.Add (new Event(-1,-1,"header",numTicksPerQuarterNote));
			byte[] MTrk = new byte[]{ 77, 84, 114, 107 };
			List<List<int>> trackHeaderIndices = findSubListFromArray (MTrk,bytes);
			int numTrackHeaders = trackHeaderIndices.Count;
			if (numTracks == numTrackHeaders && numTrackHeaders > 0) {
//				Debug.Log ("Number of tracks: " + numTracks);
				foreach (int tracknum in tracknums) {
					if (numTrackHeaders > tracknum) {
						trackHeaderIndices.Add (new List<int> (){ bytes.Length });
						byte[] trackbytes = slice (bytes, trackHeaderIndices [tracknum] [1] + 5, trackHeaderIndices [tracknum + 1] [0]);
						trackHeaderIndices.RemoveAt (trackHeaderIndices.Count - 1);
						//ok so now we have the bytes of the track we care about
						//minus the pointless 4 bytes
						//used to indicate the tracklength (which are often wrong apparently)
						//now it's just time:message pairs all the way down.
						int i = 0;
						int absoluteTime = 0;
						bool lastEventWasNoteOn = false;

						while (i < trackbytes.Length) {
							//interpret delta time
							string deltaTimeBits = "";
							string timeByte = getBits (trackbytes [i]);
							deltaTimeBits += timeByte.Substring(1);
							while (timeByte [0].Equals ('1')) {
								i++;
								timeByte = getBits (trackbytes [i]);
								deltaTimeBits += timeByte.Substring (1);
							}
							int deltaTime = Convert.ToInt32 (deltaTimeBits, 2);
							i++;
							absoluteTime += deltaTime;

							//interpret MIDI message. If you don't know how, say which message caused you a problem.
							string messageType = getBits(trackbytes[i]).Substring(0,4);
							if (messageType.Equals ("1001")) {//note on
								lastEventWasNoteOn = true;
								i++;
								int note = getIntValue (trackbytes [i]);
								i++;
								int velocity = getIntValue (trackbytes [i]);
								if (velocity == 0) {
									result.Add (new Event (note, absoluteTime, "off", tracknum));
								} else {
									result.Add (new Event (note, absoluteTime, "on", tracknum));
								}
								i++;
							} else if (messageType.Equals ("1000")) {//note off
								lastEventWasNoteOn = false;
								i++;
								int note = getIntValue (trackbytes [i]);
								i += 2;
								result.Add (new Event (note, absoluteTime, "off", tracknum));
							} else if (messageType.Equals ("1111")) {//could mean a number of things
								string fullMessage = getBits (trackbytes [i]);
								if (fullMessage.Equals ("11111111")) {//it's a meta message
									i++;
									string metaMessageType = getBits (trackbytes [i]);
									i++;
									int metaMessageLength = getIntValue (trackbytes [i]);
									if (metaMessageType.Equals ("01010001")) {//tempo change
										int endIndex = i + metaMessageLength + 1;
										string bitString = "";
										i++;
										while (i < endIndex) {
											bitString += getBits (trackbytes [i]);
											i++;
											int tempo = Convert.ToInt32 (bitString, 2);
											result.Add (new Event (-1, absoluteTime, "tempo change", tempo));
//											Debug.Log ("tempo: " + tempo + "   absoluteTime: " + absoluteTime);
										}
									} else if (metaMessageType.Equals ("01011000")) {//time signature change
										i++;
										//int timeSigNumer = getIntValue (trackbytes [i]);
										i++;
										//int timeSigDenom = getIntValue (trackbytes [i]);
										i++;
										//int timeSigClocksPerClick = getIntValue (trackbytes [i]);
										i++;
										int timeSig32ndNotesPerBeat = getIntValue (trackbytes [i]);
										i++;
										result.Add (new Event (-1, absoluteTime, "time signature change", timeSig32ndNotesPerBeat));
									} else {
										i += metaMessageLength + 1;
									}
								}
							} else if (messageType.Equals ("1100")) {//program change
								i += 2;
							} else if (messageType.Equals ("1011")) {//control change
								i += 3;
							} else if (messageType.Equals ("1101")) {//aftertouch
								i += 2;
							} else if (Convert.ToInt32 (messageType, 2) < 8) {//continuation from previous note on or note off event
								int note = getIntValue (trackbytes [i]);
								i++;
								int velocity = getIntValue (trackbytes [i]);
								if (lastEventWasNoteOn) {
									if (velocity == 0) {
										result.Add (new Event (note, absoluteTime, "off", tracknum));
									} else {
										result.Add (new Event (note, absoluteTime, "on", tracknum));
									}
								} else {
									result.Add (new Event (note, absoluteTime, "off", tracknum));
								}
								i++;
							} else {
								Debug.Log ("was unable to parse message with message type " + messageType + " at line " + i);
							}
						}
					} else {
						Debug.Log ("The file doesn't have enough tracks to have track number " + tracknum);
					}
				}
			}
			else if(numTrackHeaders < numTracks){
				Debug.Log ("The file has fewer MIDI track headers than tracks according to the file header so it's probably corrupted");
			}
			else if(numTrackHeaders > numTracks){
				Debug.Log ("the file has more track headers than tracks according to the file header. Look for a false positive");
			}
			else{
				Debug.Log ("the file has no tracks");
			}

		} else {
			Debug.Log ("That file doesn't have a proper MIDI header so either it's not a MIDI file or it's a corrupted MIDI file");
		}


		return result;
	}


	//End of methods which parse MIDI into Events







































	//Start of methods which process Events rather than MIDI

	//orders events by time they occur
	private List<Event> timeSort(List<Event> eventList){
		return eventList.OrderBy (theEvent => theEvent.time).ToList();
	}

	private List<Event> adjustForTimeSignatureChanges(List<Event> events){
		events = timeSort (events);
		int tempo = 500000;//microseconds per quarter note
		int timeSig32ndNotesPerBeat = 8;
		int pulsesPerQuarterNote = events [0].track;
		events.RemoveAt (0);

		List<EventWithMicrosecondTime> eventList = new List<EventWithMicrosecondTime> ();

		foreach (Event theEvent in events) {
			float timeToAdd = 1.0f * theEvent.time;
			timeToAdd *= tempo;
			timeToAdd *= timeSig32ndNotesPerBeat;
			timeToAdd /= 8.0f;
			timeToAdd /= 1.0f*pulsesPerQuarterNote;
			eventList.Add (new EventWithMicrosecondTime (theEvent.note, theEvent.time, theEvent.type, theEvent.track, (int)timeToAdd));
		}

		int i = 0;
		while (i < eventList.Count) {
			if (eventList [i].type.Equals ("tempo change")) {
				tempo = eventList [i].track;
//				Debug.Log ("tempo: " + tempo);
				int timeOfEventTicks = eventList [i].time;
				int timeOfEventMicroseconds = eventList [i].timeMS;
				int j = i;
				while (j < eventList.Count) {
					float timeMicroseconds = eventList [j].time;
					timeMicroseconds -= timeOfEventTicks;
					timeMicroseconds *= (1.0f * tempo * timeSig32ndNotesPerBeat) / (8 * pulsesPerQuarterNote);
					timeMicroseconds += timeOfEventMicroseconds;
					eventList[j].timeMS = (int)timeMicroseconds;
					j++;
				}
			} else if (eventList [i].type.Equals ("time signature change")) {
				if (eventList [i].track != timeSig32ndNotesPerBeat) {
					timeSig32ndNotesPerBeat = eventList [i].track;
					int timeOfEventTicks = eventList [i].time;
					int timeOfEventMicroseconds = eventList [i].timeMS;
					int j = i;
					while (j < eventList.Count) {
						float timeMicroseconds = eventList [j].time;
						timeMicroseconds -= timeOfEventTicks;
						timeMicroseconds *= (1.0f * tempo * timeSig32ndNotesPerBeat) / (8 * pulsesPerQuarterNote);
						timeMicroseconds += timeOfEventMicroseconds;
						eventList[j].timeMS = (int)timeMicroseconds;
						j++;
					}
				}
			}
			i++;
		}

		//now newTimes[i] is the time in microseconds for eventList[i]
		//Later functions are expecting Events to have microsecond time
		//so I will replace tick times in the structs with microsecond times.
		//also, I will trim out the time sig and tempo change events because they're not needed anywhere else
		events.Clear();

		i = 0;
		int lenEventList = eventList.Count;
		foreach (EventWithMicrosecondTime eventMS in eventList) {
			if (eventMS.note != -1) {
				events.Add (new Event (eventMS.note, eventMS.timeMS, eventMS.type, eventMS.track));
			}
		}

		return events;
	}

	//gets time sorted list of events pertaining to the specified note
	private List<Event> getEventsForNote(List<Event> eventList, int note)
	{
		List<Event> result = new List<Event> ();
		foreach (Event theEvent in eventList) {
			if (theEvent.note == note) {
				result.Add (theEvent);
			}
		}
		result = timeSort (result);
		return result;
	}

	//gets set of unique notes in a list of events
	private HashSet<int> getNoteSet(List<Event> eventList){
		HashSet<int> noteSet = new HashSet<int> ();
		foreach (Event theEvent in eventList) {
			noteSet.Add (theEvent.note);
		}
		return noteSet;
	}
		
	//If event list has been created from merged tracks, return version where notes that are overlapping 
	//(same note, same time region, different tracks) are put into an ordered sequence.
	//assumed to come before first and last events are labeled
	private List<Event> trimOverlappingEvents(List<Event> eventList){
		List<Event> resultList = new List<Event> ();
		HashSet<int> noteSet = getNoteSet (eventList);
		foreach (int note in noteSet) {
			List<Event> eventsForNote = getEventsForNote (eventList, note);
			int notesPlayingCurrently = 0;
			List<Event> result = new List<Event> ();
			int currentTrackPlaying = eventsForNote [0].track;
			foreach (Event theEvent in eventsForNote) {
				if (theEvent.type.Equals ("on")) {
					notesPlayingCurrently++;
					if (notesPlayingCurrently == 1) {
						result.Add (theEvent);
						currentTrackPlaying = theEvent.track;
					} else {
						result.Add (new Event (note, theEvent.time, "off", currentTrackPlaying));
						result.Add (theEvent);
					}
				} else {
					notesPlayingCurrently--;
					if (notesPlayingCurrently == 0) {
						result.Add (theEvent);
					}
					//else ignore it
				}
				if (notesPlayingCurrently == -1) {
					Debug.Log ("note is currently " + note);
					Debug.Log ("hmm, notesPlayingCurrently has somehow dipped into negatives");
				}
			}
			if (notesPlayingCurrently > 0) {
				Debug.Log ("hmm, notesPlayingCurrently is still positive at the end");
			}
			resultList.AddRange (result);
		}
		return resultList;
	}

	//does what it says. used to find out how much time should be slowed by.
	//assumes first and last events have not been labeled yet
	private int getMedianDeltaTimeBetweenOnEvents(List<Event> events)
	{
		int i = 1;
		int lastOnIndex = 0;
		List<int> deltaList = new List<int> ();
		while (i < events.Count) {
			if (events [i].type.Equals ("on")) {
				int delta = events [i].time - events [lastOnIndex].time;
				if (delta != 0) {
					deltaList.Add (delta);
					lastOnIndex = i;
				}
			}
			i++;
		}
		deltaList.Sort ();
		return deltaList [deltaList.Count / 2];
	}

	//scales time values such that median delta time between on events corresponds to a certain magic number of seconds of gameplay
	//specified by numberOfSecondsToStretchTo
	//also converts microseconds to seconds
	private List<Event> stretchTime(List<Event> events, int numberOfSecondsToStretchTo)
	{
		int medianTime = getMedianDeltaTimeBetweenOnEvents (events);
		foreach (Event theEvent in events) {
			float newTime = (1.0f * theEvent.time * 1000000 * numberOfSecondsToStretchTo) / medianTime;
			newTime /= 1000000;
			theEvent.time = (int)(newTime);
		}
		return events;
	}

	//gets amount of time note plays in the song
	//assumes overlaps have already been eliminated
	//which lets us assume even indices are on events and odd indices are off events
	public int getTimeSpentPlayingNote(List<Event> eventList, int note){ 
		int result = 0;
		List<Event> eventsForNote = getEventsForNote (eventList, note);
		int numEvents = eventsForNote.Count;
		int i = 1;
		while (i < numEvents) {
			result += eventsForNote [i].time - eventsForNote [i - 1].time;
			i += 2;
		}
		return result;
	}

	//counts how many on events correspond to each note and returns a dictionary of note:frequency pairs
	public Dictionary<int,int> countNoteFrequencies(List<Event> eventList){
		Dictionary<int,int> freqs = new Dictionary<int, int> ();
		foreach (Event theEvent in eventList) {
			if (theEvent.type.Substring (0, 2).Equals ("on")) {
				if (!(freqs.ContainsKey (theEvent.note))) {
					freqs.Add (theEvent.note, 1);
				} else {
					freqs [theEvent.note] += 1;
				}
			}
		}
		return freqs;
	}

	//starting at startTime seconds (normally where the last game ended),
	//finds the first On event and then
	//finds all events less than duration seconds after the time of that first On event.
	//and returns that slice of the array
	private List<Event> trimToInterval(List<Event> events, int startTime, int duration){
		int endTime = startTime + duration;
		int startIndex = 0;
		bool startHasBeenFound = false;
		int stopIndex = 0;
		bool stopHasBeenFound = false;
		int i = 0;
		while (i < events.Count) {
			if ((!startHasBeenFound) && events [i].time >= startTime && events [i].type.Equals ("on")) {
				startHasBeenFound = true;
				startIndex = i;
				startTime = events [i].time;
				endTime = startTime + duration;
			}
			if (events [i].time > endTime) {
				stopIndex = i;
				i = events.Count;
				stopHasBeenFound = true;
			}
			i++;
		}
		if (!startHasBeenFound) {
			Debug.Log ("trimToInterval failed - Tried to trim events starting from a time before or after the interval");
			return events;
		} else if (!stopHasBeenFound) {
			Debug.Log ("trimToInterval failed - There's not enough time in the events to have an interval that long");
			return events;
		}
		return sliceList (events, startIndex, stopIndex);
	}

	//makes it so that the time ticks begin at 0 as they would in a game
	private List<Event> normalizeTimes(List<Event> eventList)
	{
		eventList = timeSort (eventList);
		if (eventList.Count > 0) {
			int lowestTime = eventList [0].time;
			foreach (Event theEvent in eventList) {
				theEvent.time -= lowestTime;
			}
		}
		return eventList;
	}

	//returns 4 dictionaries containing note:event index pairs
	private List<Dictionary<int,int>> findFirstAndLastEventsForEachNote(List<Event> eventList)
	{
		eventList = timeSort (eventList);
		HashSet<int> noteSet = getNoteSet (eventList);
		Dictionary<int,int> notesWithFirstOnIndices = new Dictionary<int, int> ();
		Dictionary<int,int> notesWithFirstOffIndices = new Dictionary<int, int> ();
		Dictionary<int,int> notesWithLastOnIndices  = new Dictionary<int, int> ();
		Dictionary<int,int> notesWithLastOffIndices  = new Dictionary<int, int> ();
		foreach (int note in noteSet) {
			notesWithFirstOnIndices.Add (note, -1);
			notesWithFirstOffIndices.Add (note, -1);
			notesWithLastOnIndices.Add (note, -1);
			notesWithLastOffIndices.Add (note, -1);
		}
		//find first and last indices for each note
		int i = 0;
		int numEvents = eventList.Count;
		while (i < numEvents) {
			int note = eventList [i].note;
			string message = eventList [i].type;
			if (message.Equals ("on")) {
				if (notesWithFirstOnIndices [note] == -1) {
					notesWithFirstOnIndices [note] = i;
				}
				notesWithLastOnIndices [note] = i;
			} else {
				if(notesWithFirstOffIndices[note] == -1){
					notesWithFirstOffIndices [note] = i;
				}
				notesWithLastOffIndices [note] = i;
			}
			i++;
		}
		List<Dictionary<int,int>> result = new List<Dictionary<int, int>> ();
		result.Add (notesWithFirstOnIndices);
		result.Add (notesWithFirstOffIndices);
		result.Add (notesWithLastOnIndices);
		result.Add (notesWithLastOffIndices);
		return result;
	}

	//returns an edited version of eventList such that the first on and off events for each note are labeled as such
	//and so are the last on and off events
	//assumes duplicate and overlapping events have been trimmed away
	//also resolves situations where trimToInterval caused Off event to be first or On event to be last for a note
	private List<Event> labelFirstAndLastEventsForEachNote(List<Event> eventList, int duration){
		List<Dictionary<int,int>> dicts = findFirstAndLastEventsForEachNote (eventList);
		Dictionary<int,int> notesWithFirstOnIndices = dicts [0];
		Dictionary<int,int> notesWithFirstOffIndices = dicts [1];
		Dictionary<int,int> notesWithLastOnIndices = dicts [2];
		Dictionary<int,int> notesWithLastOffIndices = dicts [3];
		HashSet<int> noteSet = getNoteSet (eventList);

		//label events accordingly. Spit out some debug cases
		foreach (int note in noteSet) {
			int firstOnIndex = notesWithFirstOnIndices [note];
			int firstOffIndex = notesWithFirstOffIndices [note];
			int lastOnIndex = notesWithLastOnIndices [note];
			int lastOffIndex = notesWithLastOffIndices [note];
			if (lastOffIndex == -1 || firstOffIndex == -1) {
				eventList [firstOnIndex].type = "on for the first and last time";
				int trackOfOnEvent = eventList [firstOnIndex].track;
				eventList.Add (new Event (note, duration, "off for the first and last time", trackOfOnEvent));
			} else if (firstOnIndex == -1 || lastOnIndex == -1) {
				eventList [firstOffIndex].type = "off for the first and last time";
				int trackOfOffEvent = eventList [firstOffIndex].track;
				eventList.Add (new Event (note, 0, "on for the first and last time", trackOfOffEvent));
			} else if (firstOffIndex < firstOnIndex) {
				int trackOfOffEvent = eventList [firstOffIndex].track;
				eventList [firstOffIndex].type = "off for the first time";
				eventList.Add (new Event (note, 0, "on for the first time", trackOfOffEvent));
				eventList [lastOnIndex].type = "on for the last time";
				eventList [lastOffIndex].type = "off for the last time";
			} else if (lastOnIndex > lastOffIndex) {
				int trackOfOnEvent = eventList [lastOnIndex].track;
				eventList [lastOnIndex].type = "on for the last time";
				eventList.Add (new Event (note, duration, "off for the last time", trackOfOnEvent));
				eventList [firstOnIndex].type = "on for the first time";
				eventList [firstOffIndex].type = "off for the first time";
			} else {
				if (firstOnIndex == lastOnIndex) {
					eventList [firstOnIndex].type = "on for the first and last time";
				} else {
					eventList [firstOnIndex].type = "on for the first time";
					eventList [lastOnIndex].type = "on for the last time";
				}
				if (firstOffIndex == lastOffIndex) {
					eventList [firstOffIndex].type = "off for the first and last time";
				} else {
					eventList [firstOffIndex].type = "off for the first time";
					eventList [lastOffIndex].type = "off for the last time";
				}
			}
		}
		return eventList;
	}

	private void printAllEvents(List<Event> events){
		Debug.Log ("eventList.Count: " + events.Count);
		foreach (Event theEvent in events) {
			Debug.Log (theEvent.note + " " + theEvent.time + " " + theEvent.type + " " + theEvent.track);
		}
	}
}
