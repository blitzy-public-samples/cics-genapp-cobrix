******************************************************************
*  COPYBOOK  : GFCOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : CO
******************************************************************
 01  RT-FCO-RATING.

          03 RT-FCO-TERRITORY-CODE            PIC X(3).
          03 RT-FCO-CLASS-CODE                PIC X(4).
          03 RT-FCO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FCO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FCO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FCO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FCO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FCO-RATED-PREMIUM             PIC 9(9)V9(2).
