# Rejestrator Dźwięku

Rejestrator dźwięku to aplikacja GUI w Pythonie, która umożliwia nagrywanie dźwięku z wybranego urządzenia wejściowego oraz zapisywanie plików WAV według wybranych parametrów. Program obsługuje ręczny wybór urządzenia wejściowego, ustawienia tonu i pozycji oraz automatyczne numerowanie plików w przypadku istniejących nagrań.

## Funkcje
- Wybór urządzenia wejściowego
- Wybór tonu i pozycji dla zapisywanego pliku
- Automatyczna numeracja plików
- Wyświetlanie liczby już istniejących plików
- Obsługa nagrywania przyciskiem GUI oraz klawiszem **Enter**

## Instalacja i uruchomienie
1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/cyptrix12/Guitar_Recorder_for_project.git
   cd Guitar_Recorder_for_project
   ```
2. Utwórz i aktywuj wirtualne środowisko:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate    # Windows
   ```
3. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```
4. Uruchom program:
   ```bash
   python main.py
   ```

## Używanie aplikacji
1. Wybierz **urządzenie wejściowe** z listy rozwijanej.
2. Wybierz **ton** (np. A, C, E, G).
3. Wybierz **pozycję** (np. "otwarta", "barowe_e").
4. Sprawdź liczbę już istniejących plików dla danej kombinacji.
5. Kliknij **"Rozpocznij nagrywanie"** lub naciśnij **Enter**, aby rozpocząć nagrywanie.
6. Kliknij **"Zakończ nagranie"** lub ponownie naciśnij **Enter**, aby zakończyć nagrywanie.
7. Plik zostanie zapisany (wraz z numeracją) automatycznie.
