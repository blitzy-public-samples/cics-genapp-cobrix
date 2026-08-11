******************************************************************
*  COPYBOOK  : GOOKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : OK
******************************************************************
 01  RT-OOK-RATING.

          03 RT-OOK-TERRITORY-CODE            PIC X(3).
          03 RT-OOK-CLASS-CODE                PIC X(4).
          03 RT-OOK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OOK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OOK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OOK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OOK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OOK-RATED-PREMIUM             PIC 9(9)V9(2).
