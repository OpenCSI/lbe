Documentation is available at https://dev.opencsi.com/projects/ldbe/wiki

Internal object JSON representation used by LBE:

	{
		_id: bbonfils,
		displayName: 'Bruno Bonfils',
		version: 2,
		update_at:
		create_at:
		sync_at:
		status:
		attributes: {
			cn: [ 'Bruno Bonfils' ],
			sn: [ 'Bonfils' ],
			givenName: [ 'Bruno' ],
			mail: [ 'bbonfils@opencsi.com' ],
			uid: [ 'bbonfils' ],
		},
		lastsynclog: [ 'Some text message', 'another one' ]
		versions: {
			1: { cn: ['bruno bonfils'], sn: [ 'bonfils' ], [..] },
			0: { cn: ['bruno bonfils'], sn: [ 'bonfils' ], [..] }
		}
	}

Reconciliation:

Diagram sequence (use with http://www.websequencediagrams.com/)

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
