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
		opsAttributes: {
			cn: { create_at: 20120234242, update_at:  20120234242},
			sn: { create_at: 20120234242, update_at:  20120234242},
			[..]
		}
		lastsynclog: [ 'Some text message', 'another one' ]
		versions: {
			1: { cn: ['bruno bonfils'], sn: [ 'bonfils' ], [..] },
			0: { cn: ['bruno bonfils'], sn: [ 'bonfils' ], [..] }
		}
	}


Modification d'un objet:
 - 

Algo de réconciliation LBE -> Annuaire:

 - Recherche des objets avec update_at > sync_at
 - On parse les attributes pour vérifier si update_at > sync_at
 - Création du changeset
 - Si mise à jour dans le target ok: mise à jour de sync_at
 - Sinon: 