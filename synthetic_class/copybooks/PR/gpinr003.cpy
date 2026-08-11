******************************************************************
*  COPYBOOK  : GPINR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : IN
******************************************************************
 01  RT-PIN-RATING.

          03 RT-PIN-TERRITORY-CODE            PIC X(3).
          03 RT-PIN-CLASS-CODE                PIC X(4).
          03 RT-PIN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PIN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PIN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PIN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PIN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PIN-RATED-PREMIUM             PIC 9(9)V9(2).
