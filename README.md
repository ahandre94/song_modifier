# Song modifier
Script per modificare e alterare tracce audio da linea di comando. Cosa puoi fare?
Cambiare la tonalità! Dividere la traccia audio in vocale e strumentale! Cambiare
il formato output!

## Installazione
Questa guida è fatta principalmente per chi utilizza Windows.
Per utilizzare lo script è necessario scaricare Python, FFmpeg e Rubber Band e
configurarli correttamente.

#### Python
Scaricare l'ultima release di Python (https://www.python.org/downloads/) e installarla.
Lo script è testato con la versione 3.10.

#### FFmpeg
Una volta scaricata l'ultima release (https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z),
estrarre il contenuto in una cartella chiamata `ffmpeg` e copiarla in `C:`. A questo
punto eseguire come amministratore il terminale (cmd -> Esegui come amministratore)
e dare il seguente comando per aggiungere FFmpeg al PATH.

`setx /m PATH "C:\ffmpeg\bin;%PATH%"`

Sarà necessario riavviare il computer.

#### Rubber Band
Una volta scaricata l'ultima release (https://breakfastquay.com/files/releases/rubberband-3.0.0-gpl-executable-windows.zip),
estrarre il contenuto in una cartella chiamata `rubberband` e copiarla in `C:`. A questo
punto eseguire come amministratore il terminale (cmd -> Esegui come amministratore)
e dare il seguente comando per aggiungere Rubber Band al PATH.

`setx /m PATH "C:\rubberband;%PATH%"`

Sarà necessario riavviare il computer.

#### CUDA Toolkit
Se si ha una GPU NVIDIA, per TensorFlow è necessario (anche se non obbligatorio)
scaricare il CUDA Toolkit (https://developer.nvidia.com/cuda-downloads) e installarlo.

## Preparazione
Prima di eseguire effettivamente lo script è necessario creare l'ambiente virtuale
e installare le dipendenze per Python.

Per ottenere il path di Python si può usare il comando `where python` che darà un
risultato simile a `C:\Users\%USERNAME%\AppData\Local\Programs\Python\%Python3x%\python.exe`.

Da terminale:
```
> pip install virtualenv
> virtualenv --python C:\Users\%USERNAME%\AppData\Local\Programs\Python\%Python3x%\python.exe song_modifier
> cd song_modifier
```

Copiare lo script all'interno della cartella appena creata e proseguire con l'attivazione
del venv e l'installazione dei pacchetti.
```
> .\Scripts\activate
> pip install -r requirements.txt
```

Se si possiede una GPU NVIDIA e si è installato il CUDA Toolkit, installare anche
i pacchetti richiesti.
```
> pip install -r requirements_cuda.txt
```

## Esecuzione
Sempre da terminale e con il venv attivato:
```
> python main.py [-h] [-a AUDIO] [-p PITCH] [-s] [-f FORMAT] [-o OUTPUT] [-d]
```

L'argomento `-a` (`--audio`) specifica il path al file audio da modificare (obbligatorio).
L'argomento `-p` (`--pitch`) specifica di quanti semitoni alterare la traccia (+1, -1, ...).
L'argomento `-s` (`--split`) specifica se dividere la traccia audio in vocale e strumentale.
L'argomento `-f` (`--format`) specifica il formato di output (wav, webm, mp3, m4a, flac).
L'argomento `-o` (`--output`) specifica la cartella di output (nel caso non esista, viene creata).
L'argomento `-d` (`--debug`) attiva il debug mode.
Se necessario usare l'argomento `-h` per mostrare le varie opzioni.

Esempio:
```
> python main.py -a C:\Users\my-name\Music\my-song.flac -p 3 -s -f m4a -o C:\Users\my-name\Music\modified
```
La traccia audio `my-song.flac` verrà aumentata di 1 tono e mezzo (3 semitoni),
divisa in traccia vocale e strumentale e salvata in formato m4a nella cartella
`modified`.
