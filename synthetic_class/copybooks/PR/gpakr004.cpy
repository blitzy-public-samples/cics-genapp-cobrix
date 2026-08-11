******************************************************************
*  COPYBOOK  : GPAKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : AK
******************************************************************
 01  RT-PAK-RATING.

          03 RT-PAK-TERRITORY-CODE            PIC X(3).
          03 RT-PAK-CLASS-CODE                PIC X(4).
          03 RT-PAK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PAK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PAK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PAK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PAK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PAK-RATED-PREMIUM             PIC 9(9)V9(2).
