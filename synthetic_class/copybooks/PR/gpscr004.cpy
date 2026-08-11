******************************************************************
*  COPYBOOK  : GPSCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : SC
******************************************************************
 01  RT-PSC-RATING.

          03 RT-PSC-TERRITORY-CODE            PIC X(3).
          03 RT-PSC-CLASS-CODE                PIC X(4).
          03 RT-PSC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PSC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PSC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PSC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PSC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PSC-RATED-PREMIUM             PIC 9(9)V9(2).
