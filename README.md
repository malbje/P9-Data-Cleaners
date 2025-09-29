# P9-Data-Cleaners
README bruges som et "opslagsværk" til vores struktur for kode. 

--- Generelle guidelines ---

* Vi bruger ikke forkortelser i vores kode - funktioner skal være besrkevet udførligt for at andre gruppemedlemmer kan forstå uden at skulle konsulterer med skribent.

    IN CASE at man laver en forkortelse, skal den beskrives udførligt og tydeligt.

* Øverst i samtlige filer kræves en forklaring af filens funktion og formål
    Se eksempel:
    # -----------------------------
    # This page works with creating and sending notifications based on 
    # 
    # Currently it is printing 3 reminders in the terminal based on the mock data
    # -----------------------------

* Alt ud over vores README foregår på engelsk, thx


* Alle filers navne skal være deskriptive (atomiske) for deres funktion. Heller et langt navn end et forvirende. 


* Vi skal beskrive alle funktioner så de er let forståelige, i samme stilart. 
    Vi bruger google style docstrings som ligner javadoc i python eksempel: 

        def function_name(arg1, arg2):

            """
            Short description of what the function does.

            Args:
                arg1 (type): Description of the first argument.
                arg2 (type): Description of the second argument.

            Returns:
                type: Description of what is returned.

        """

* Når filer referer på tværs, beskriv referencen. Hvor er den, hvad er funktionen? Hvorfor?

* 