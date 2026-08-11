******************************************************************
*  COPYBOOK  : GPILR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : IL
******************************************************************
 01  RT-PIL-RATING.

          03 RT-PIL-TERRITORY-CODE            PIC X(3).
          03 RT-PIL-CLASS-CODE                PIC X(4).
          03 RT-PIL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PIL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PIL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PIL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PIL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PIL-RATED-PREMIUM             PIC 9(9)V9(2).
