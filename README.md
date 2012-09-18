Documentation is available at https://dev.opencsi.com/projects/ldbe/wiki

Internal object JSON representation used by LBE:

	{
		_id: 'Bruno Bonfils',           # Value of ObjectTemplate.instanceUniqueName attribute
		displayName: 'Bruno Bonfils',   # Value of ObjectTemplate.instanceDisplayName attribute
		version: 2,                     # Current version
		updated_at:                     # Timestamp of last object modification in *backend*
		created_at: datetime,           # Timestamp of object creation in *backend*
		sync_at: datetime,              # Timestamp of last object changed in *target*
		status:                         # check directory/models.py for available status
		attributes: {
			cn: [ 'Bruno Bonfils' ],
			sn: [ 'Bonfils' ],
			givenName: [ 'Bruno' ],
			mail: [ 'bbonfils@opencsi.com' ],
			uid: [ 'bbonfils' ],
		},
		changes: {                      # Special sections, defined which changes must be applied to the target
		    type:                       # check directory/models for available change type
		    set: {
		        mail: [ 'newvalue@opencsi.com' ],
		    }
		}
		lastsynclog: [ 'Some text message', 'another one' ]
		versions: {
			1: { cn: ['bruno bonfils'], sn: [ 'bonfils' ], [..] },
			0: { cn: ['bruno bonfils'], sn: [ 'bonfils' ], [..] }
		}
	}

Reconciliation:

Diagram sequence (use with http://www.websequencediagrams.com/)

<<<<<<< HEAD
http://www.websequencediagrams.com/cgi-bin/cdraw?lz=dGl0bGUgUmVjb25jaWxpYXRpb24KcGFydGljaXBhbnQgQXBwIGFzIGEACA1UYXJnZXQgYXMgdAAgDUJhY2tlbmQgYXMgYgoKYS0-YjogR2V0IGFsbCBvYmplY3RzIHRvIHVwZGF0ZQpiLT5hOiByZXR1cm4gc2VhcmNoKAAgBi5zdGF0dXMgPSBBV0FJVElOR19TWU5DKQphbHQgRm9yZWFjaABKBwphAEEFY3JlYXRlIGEgY2hhbmdlIHNlABUFdDogQXBwbHkAEAcADwdiOiBVAH4FAIEOByAoc3RhdGUgPSBTWU5DRUQsIHN5bmNlZF9hdCA9IG5vdykKZW5kCgo&s=modern-blue

title Reconciliation
participant App as a
participant Target as t
participant Backend as b

a->b: Get all objects to update
b->a: return search(object.status = AWAITING_SYNC)
alt Foreach object
a->a: create a change set
a->t: Apply changeset
a->b: Update object (state = SYNCED, synced_at = now)
end
=======
Global TODO:
 - For the moment, we search all objects to sync by using the status (OBJECT_STATE_AWAITING_SYNC), however we can also use synced_at, which is the better?
 - The backend-import-data task doesn't manage very well object create by LBE in the target, need improvements
>>>>>>> c3457ff23dce7790945cde52968afd1bd1b71bdc
