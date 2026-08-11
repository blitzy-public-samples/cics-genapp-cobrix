******************************************************************
*  COPYBOOK  : GFDER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : DE
******************************************************************
 01  RT-FDE-RATING.

          03 RT-FDE-TERRITORY-CODE            PIC X(3).
          03 RT-FDE-CLASS-CODE                PIC X(4).
          03 RT-FDE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FDE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FDE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FDE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FDE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FDE-RATED-PREMIUM             PIC 9(9)V9(2).
