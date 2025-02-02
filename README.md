# Guitar Recorder for project

Guitar_Recorder_for_project to aplikacja GUI w Pythonie, która umożliwia nagrywanie dźwięku z wybranego urządzenia wejściowego oraz zapisywanie plików WAV według wybranych parametrów. Program obsługuje ręczny wybór urządzenia wejściowego, ustawienia akordu, pozycji, modelu gitary, ustawień pokręteł oraz ID grającego, a także automatyczne numerowanie plików w przypadku istniejących nagrań.

## Funkcje
- Wybór urządzenia wejściowego
- Wybór modelu gitary
- Wybór nazwy akordu
- Wybór pozycji
- Wybór ustawień pokręteł
- Wybór ID grającego
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
2. Wybierz **model gitary** (np. 1, 2, 3, 4, 5).
3. Wybierz **nazwę akordu** (np. A, C, E, G).
4. Wybierz **pozycję** (np. "otwarta", "barowe_e").
5. Wybierz **ustawienia pokręteł** (np. 1, 2, 3, 4).
6. Wybierz **ID grającego** (np. 1, 2, 3, 4, 5).
7. Sprawdź liczbę już istniejących plików dla danej kombinacji.
8. Kliknij **"Rozpocznij nagrywanie"** lub naciśnij **Enter**, aby rozpocząć nagrywanie.
9. Kliknij **"Zakończ nagranie"** lub ponownie naciśnij **Enter**, aby zakończyć nagrywanie.
10. Plik zostanie zapisany automatycznie w formacie: `ModelGitary_NazwaAkordu_Pozycja_UstawieniePokretel_IdGrajacego_Numeracja.wav`.
