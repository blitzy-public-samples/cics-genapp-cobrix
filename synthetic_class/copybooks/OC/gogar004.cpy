******************************************************************
*  COPYBOOK  : GOGAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : GA
******************************************************************
 01  RT-OGA-RATING.

          03 RT-OGA-TERRITORY-CODE            PIC X(3).
          03 RT-OGA-CLASS-CODE                PIC X(4).
          03 RT-OGA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OGA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OGA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OGA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OGA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OGA-RATED-PREMIUM             PIC 9(9)V9(2).
