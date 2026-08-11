******************************************************************
*  COPYBOOK  : GPOKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : OK
******************************************************************
 01  RT-POK-RATING.

          03 RT-POK-TERRITORY-CODE            PIC X(3).
          03 RT-POK-CLASS-CODE                PIC X(4).
          03 RT-POK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-POK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-POK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-POK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-POK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-POK-RATED-PREMIUM             PIC 9(9)V9(2).
