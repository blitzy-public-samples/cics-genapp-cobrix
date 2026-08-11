******************************************************************
*  COPYBOOK  : GFSCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : SC
******************************************************************
 01  RT-FSC-RATING.

          03 RT-FSC-TERRITORY-CODE            PIC X(3).
          03 RT-FSC-CLASS-CODE                PIC X(4).
          03 RT-FSC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FSC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FSC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FSC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FSC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FSC-RATED-PREMIUM             PIC 9(9)V9(2).
