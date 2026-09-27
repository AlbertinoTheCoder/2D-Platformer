# Piano di implementazione

## Stato e vincoli

Preparazione offline richiesta dall'utente. Non avviare Unreal, non connettersi a MCP e non creare un progetto basato su una versione presunta prima del suo via.
Il workspace iniziale contiene soltanto `Docs/promptstart.md`; nessun `.uproject`, asset o modulo C++ disponibile. `Docs/Prompt.MD`, citato nell'IDE, non è presente su disco.
Il brief originale rimane la specifica funzionale. I file qui preparati sono input di lavoro: non costituiscono un gioco già implementato né asset Unreal importabili direttamente.

## Decisioni iniziali

- Coordinate in centimetri: movimento X, profondità Y bloccata, altezza Z. Camera ortografica rivolta verso il piano XZ.
- Blueprint modulari e CharacterMovement come base; Paper2D per rappresentazione e stati visivi. Enhanced Input per tutti i comandi.
- Parametri e posizioni in `Config/platformer.json`. Quel file è un manifesto offline, non un file di configurazione nativo Unreal.
- Cartella asset `/Game/Platformer`; sottocartelle del brief più `Input`. Nessuna sovrascrittura di contenuti estranei.
- C++ soltanto se necessario dopo aver verificato versione, toolchain e capacità MCP. Non generare `.uasset` fittizi o grafi serializzati con formati presunti.

## Fasi e criteri di uscita

1. **Ispezione dopo il via:** identificare progetto attivo, versione reale dell'editor, plugin Paper2D/Enhanced Input, mappe, impostazioni input, strumenti MCP disponibili e capacità di creazione grafi/UMG. Inventariare collisioni e asset esistenti. Verificare salvataggio e compilazione su un asset minimo prima delle dipendenze successive.
2. **Fondamenta:** creare struttura, interfaccia danno, componente salute e feedback; input e GameMode/Controller/GameState. Compilare e salvare per piccoli gruppi. Tutti i riferimenti devono risolversi.
3. **Vertical slice movimento:** stanza temporanea, player, camera, accelerazione/frenata, salto variabile, coyote e buffer. Provare PIE prima di costruire il livello completo.
4. **Ciclo di vita:** danno, invulnerabilità, morte, checkpoint, respawn, hazard e kill zone. Verificare che la morte scatti una sola volta e che il respawn liberi tutti i blocchi di controllo.
5. **Interazioni:** monete, HUD, pattuglia, stomp e attacco, piattaforma mobile. Provare ogni attore isolatamente, poi insieme al player.
6. **Livello completo:** generare geometria dal manifesto, tutorial iniziale, combattimento, checkpoint, tratto mobile e finale. Correggere distanze con misure reali in PIE.
7. **UI e feedback:** pausa, morte, completamento, restart, stati animazione e hook audio. Verificare input gamepad, focus UI e ridimensionamento.
8. **Consegna giocabile:** percorso completo dall'inizio alla fine, compilazione Blueprint, salvataggio, riapertura mappa e nuovo PIE. Registrare risultati e limiti effettivi.

## Contratti dei sistemi

| Sistema | Responsabilità e comunicazione |
|---|---|
| BPC_Health | HP, invulnerabilità con timer, eventi HealthChanged/Damaged/Died; morte emessa una volta. Kill zone usa una funzione di morte esplicita che ignora invulnerabilità. |
| BPI_Damageable | Punto di ingresso comune per danno da attacco, contatto e hazard; delega al componente salute. |
| BP_Player | Input, locomozione, facing, stato animazione, attacco dedicato; nessuna gestione diretta dei widget. |
| BP_PlatformerGameState | Monete e stato Playing/Dead/Complete; eventi per UI. Monete raccolte e nemici sconfitti persistono dopo respawn; restart ricarica e azzera il livello. |
| BP_PlatformerController | Mapping context, camera, creazione UI e focus, pausa/ripresa/restart. Pausa disponibile anche a gioco sospeso. |
| BP_Checkpoint | Trasformazione respawn con capsule libera; attiva il nuovo checkpoint e spegne il precedente. Fallback allo spawn iniziale. |
| BP_PatrolEnemy | Limiti pattuglia, probe muro/bordo, contatto, morte; stomp riconosciuto prima del danno da contatto. |
| BP_MovingPlatform | Superficie bloccante mobile, estremi, velocità, attesa e ping-pong. Usare movement base del CharacterMovement, non attachment manuale del player. |
| BPC_Feedback | Eventi Jump/Land/Coin/Damage/EnemyDeath/Checkpoint/Complete, suoni opzionali e feedback visivo sostituibile. |

## Algoritmi da tradurre in Blueprint

Salto: conservare timestamp dell'ultimo contatto a terra e della pressione Jump. Una richiesta può essere consumata quando grounded oppure entro coyote, e soltanto se il salto corrente non è stato già consumato. In atterraggio riarmare e consumare l'eventuale buffer valido; distinguere caduta da bordo e salto volontario per evitare doppi salti. Non affidarsi al solo `CanJump` predefinito per il coyote. Il rilascio taglia la velocità Z positiva una sola volta; una richiesta bufferizzata conserva lo stato del pulsante, così un tap già rilasciato produce un salto corto. Cancellare timestamp su morte, respawn e completamento.

Gravità: valore base in salita, moltiplicatore in discesa, ripristino ad atterraggio/respawn. Convertire l'accelerazione assoluta configurata in GravityScale usando la gravità reale del mondo ispezionato. Non sommare impulsi ogni frame.

Attacco: cooldown e finestra attiva separati; box/trace davanti al facing, filtro Damageable e insieme dei bersagli già colpiti per singolo attacco. Debug disattivato di default. Stomp richiede discesa e contatto sulla parte superiore del nemico, poi rimbalzo controllato.

Hazard: un overlap iniziale e timer durante permanenza permettono nuovi danni dopo invulnerabilità; annullare timer all'uscita/distruzione. Monete disabilitano collisione prima di emettere raccolta, evitando doppio conteggio.

Pausa: input Pause eseguibile durante pausa, focus sul pulsante Resume, corretta modalità input al ritorno. Restart riapre solo la mappa corrente. Quit interrompe PIE tramite capacità editor disponibili, senza chiudere l'editor; in build termina il gioco.

Collisioni: terreno blocca Pawn; monete/checkpoint/goal overlap solo player; attacco ignora terreno e player. Confermare preset esistenti prima di creare canali. Capsule resta invariata durante squash/stretch: deformare solo la rappresentazione.

Tick limitato a movimento/camera/piattaforme e logiche che lo richiedono; salute, UI, checkpoint e feedback guidati da eventi/timer.

## Layout e verifica offline

Lo script calcola apice e gittata con gravità distinta salita/discesa. Riserva il 20% della gittata teorica e aggiunge il diametro capsule al gap. Assume salto tenuto e velocità orizzontale massima: non dimostra giocabilità con accelerazione, collisioni o piattaforma in moto. Il ponte si attraversa aspettando e viaggiando sulla piattaforma, non saltando direttamente il vuoto.

## Verifiche obbligatorie in editor

- Spawn corretto automatico e movimento su piano; A/D, frecce e gamepad.
- Salto corto/lungo distinguibili; coyote a 0,10 s valido e a 0,16 s scaduto; buffer a 0,10 s prima dell'atterraggio valido e a 0,16 s scaduto, con tolleranza di un frame.
- Nessun doppio salto; prove a 30/60/120 fps; camera fluida, nessuna rotazione inattesa.
- Collisioni solide, salto sotto piattaforma, trasporto della piattaforma mobile e ripartenza ai suoi estremi.
- Raccolta unica, contatore corretto, HP/HUD aggiornati, invulnerabilità e danno continuato su spike.
- Morte per HP e kill zone, messaggio, respawn senza input residuo; ultimo checkpoint e fallback iniziale.
- Pattuglia con inversione a muro/limite/bordo; contatto, stomp, attacco e cooldown senza doppi danni.
- Pausa/ripresa anche da gamepad, restart durante pausa, Quit sicuro in PIE; HUD a 1280×720, 1920×1080 e ultrawide.
- Goal blocca gameplay, mostra totale raccolto, permette restart; nessun trigger di morte dopo Complete.
- Tutti gli stati Idle/Run/Jump/Fall/Attack/Hurt/Death raggiungibili, hook audio senza asset null problematici.
- Percorso completo giocabile, nessun errore Blueprint significativo, asset salvati e riferimenti validi dopo riapertura.
