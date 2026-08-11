******************************************************************
*  COPYBOOK  : GOCAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : CA
******************************************************************
 01  RT-OCA-RATING.

          03 RT-OCA-TERRITORY-CODE            PIC X(3).
          03 RT-OCA-CLASS-CODE                PIC X(4).
          03 RT-OCA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OCA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OCA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OCA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OCA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OCA-RATED-PREMIUM             PIC 9(9)V9(2).
