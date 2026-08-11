******************************************************************
*  COPYBOOK  : GUIDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : ID
******************************************************************
 01  RT-UID-RATING.

          03 RT-UID-TERRITORY-CODE            PIC X(3).
          03 RT-UID-CLASS-CODE                PIC X(4).
          03 RT-UID-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UID-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UID-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UID-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UID-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UID-RATED-PREMIUM             PIC 9(9)V9(2).
