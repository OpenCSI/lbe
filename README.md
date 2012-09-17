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


Global TODO:
 - For the moment, we search all objects to sync by using the status (OBJECT_STATE_AWAITING_SYNC), however we can also use synced_at, which is the better?
 - The backend-import-data task doesn't manage very well object create by LBE in the target, need improvements
