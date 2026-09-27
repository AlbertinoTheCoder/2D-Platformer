# Platformer 2D — preparazione offline

Specifica: [Docs/promptstart.md](Docs/promptstart.md). Piano: [Docs/implementation-plan.md](Docs/implementation-plan.md).

Nessuna connessione a Unreal è necessaria per questi comandi (Python 3, nessuna dipendenza esterna):

```powershell
python Scripts/inspect_workspace.py
python Scripts/prepare_platformer.py --check
python Scripts/prepare_platformer.py
```

Il primo comando legge i descrittori `.uproject` eventualmente presenti. Il secondo controlla parametri e distanze; il terzo genera `Build/Preparation/platformer_plan.json` con asset pianificati, layout e verifica teorica dei salti. La rigenerazione sostituisce solo quel report derivato: modificare `Config/platformer.json` per cambiare il progetto.

Questi script non avviano l'editor, non usano MCP e non creano asset Unreal. L'integrazione, la creazione dei Blueprint e i test PIE inizieranno al via dell'utente, dopo aver identificato versione e progetto.
